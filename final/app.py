"""
A simple python flask application to generate captions for your paintings, Inspired by Microsoft's captionBot.
Modelled after ML - flex & Vision labwork
"""

from flask import redirect, request, url_for, render_template, Flask
from datetime import datetime
import logging

from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech

#CLOUD_STORAGE_BUCKET = os.getenv("CLOUD_STORAGE_BUCKET")
CLOUD_STORAGE_BUCKET = "icsbucket2"
app = Flask(__name__)       # our Flask app
@app.route("/", methods=["GET"])
def index():

    '''
    This is the landing page which takes the GET request and returns all the images/paintings processed so far
    '''
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind="Images")
    image_entities = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return render_template("index.html", image_entities=image_entities)


@app.route("/upload_photo", methods=["GET", "POST"])
def upload_photo():
    image = request.files["file"]

    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(image.filename)
    blob.upload_from_string(image.read(), content_type=image.content_type)

    # Make the blob publicly viewable.
    blob.make_public()

    # Create a Cloud Vision client.
    vision_client = vision.ImageAnnotatorClient()

    # Use the Cloud Vision client to generate caption for our images/paintings located in google cloud storage
    source_uri = "gs://{}/{}".format(CLOUD_STORAGE_BUCKET, blob.name)
    # create Image object and specify the location of the image
    image = vision.Image(source=vision.ImageSource(gcs_image_uri=source_uri))
    
    #use label detection to get all the labels of the image
    response = vision_client.label_detection(image=image)
    #get label annotation portion of the labels
    labels = response.label_annotations
    
    # we only need label descriptons
    label_descriptions=""

    for label in labels:
        label_descriptions = label_descriptions + label.description + ", "

    # Get the best guess label for our paintings/images
    response1 = vision_client.web_detection(image=image)
    label = response1.web_detection.best_guess_labels
    caption = label[0].label
    
    
    # Some of the labels are not in english. Use translate api to convert the text in en. 
    
    # create translate Client object
    translate_client = translate.Client()
    translation = translate_client.translate(caption, target_language='en')
    if translation['translatedText'] =="painting" or translation['translatedText'] =="art":
        caption = "I think it's " +  translation['translatedText']
    else:
        caption = "I think this painting describes " +  translation['translatedText']
    


    # Use the Text-to-Speech API to convert a string into audio data.
    # Reference: https://codelabs.developers.google.com/codelabs/cloud-text-speech-python3#8

    #initate a text to speech client
    t2s_client = texttospeech.TextToSpeechClient()
    text_input = texttospeech.SynthesisInput(text=caption)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code='en-US', name='en-US-Standard-B', ssml_gender='MALE'
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response2 = t2s_client.synthesize_speech(
       input=text_input, voice=voice_params, audio_config=audio_config
    )

    filename = "t2s.mp3"
    with open(filename, "wb") as out:
        out.write(response2.audio_content)
    
    #create a blob for the audio file
    audio_blob = bucket.blob(caption+'.mp3')
    # upload the mp3 file just now created
    audio_blob.upload_from_filename(filename)

    # Make the blob publicly viewable.
    audio_blob.make_public()

    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    current_datetime = datetime.now()
    
    # The kind for the new entity.
    kind = "Images"

    # The name/ID for the new entity.
    name = blob.name

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind, name)

    # Construct the new entity using the key. 
    entity = datastore.Entity(key)
    
    #Set dictionary values for entity keys blob_name, image_public_url, timestamp, caption, label_descriptions and audio_public_url
    entity["blob_name"] = blob.name
    entity["image_public_url"] = blob.public_url
    entity["timestamp"] = current_datetime
    entity["caption"] = caption
    entity["label_descriptions"] = label_descriptions
    entity["audio_public_url"] = audio_blob.public_url
    # Save the new entity to Datastore.
    datastore_client.put(entity)

    return redirect("/result")

@app.route("/result", methods=["GET"])
def result():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind="Images")
    # sort them by timestamp in descending order to get the latest image processed
    query.order = ["-timestamp"]
    response = list(query.fetch())
    if not response:
        return redirect("/")
    # Return a Jinja2 HTML template and pass in response[0] as a parameter.
    return render_template("result.html", response=response[0])

@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occurred during a request.")
    return (
        """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(
            e
        ),
        500,
    )
    
if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=8000, debug=True)
