from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image, ImageDraw
from . import models
from .timeout import timeout

config = models.Config.objects.filter(id=1).values()[0]

origin_path = config['origin_path']
aux_path = config['aux_path']
final_path = config['final_path']


@timeout(5.0)
def analyze_image(backend, screnshot_name):
    account_key = backend['account_key']
    account_name = backend['account_name']
    account_region = backend['account_region']
    resource_group = backend['resource_group']
    
    credentials = CognitiveServicesCredentials(account_key)
    client = ComputerVisionClient(
        endpoint="https://" + account_region + ".api.cognitive.microsoft.com/",
        credentials=credentials
    )
    max_retries = 1
    retries = max_retries
    response_ok = False
    screnshot_path = origin_path + '/' + screnshot_name
    image = open(screnshot_path, 'rb')
    remote_image_features = ['objects']
    objects = list()
    while not response_ok and retries > 0:
        try:
            objects = client.analyze_image_in_stream(image, remote_image_features)
            objects = objects.as_dict()['objects']
            response_ok = True
        except Exception:
            retries -= 1
    return objects

def get_persons(analized_image):
    persons = list()
    if len(analized_image) > 0:
        for detected_object in analized_image:
            object_property = detected_object['object_property']
            if 'person' in object_property:
                persons.append(detected_object)
    return persons

def draw_rectangle(persons, screnshot_name):
    if len(persons) > 0:
        screnshot_path = origin_path + '/' + screnshot_name
        image = Image.open(screnshot_path)
        image_post = ImageDraw.Draw(image)
        for person in persons:
           rectangle =  person['rectangle']
           x0 = rectangle['x']
           y0 = rectangle['y']
           x1 = x0 + rectangle['w']
           y1 = y0 + rectangle['h']
           shape = [(x0, y0), (x1, y1)]
           image_post.rectangle(shape, outline='red', width=6)
        screnshot_final_path = final_path + '/' + screnshot_name
        image.save(screnshot_final_path)   
        return True
    else:
        return False



