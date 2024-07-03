from django.test import TestCase
from key_images_app.services.keyimage_service import KeyImageService

# Create your tests here.
class KeyImagesTestCase(TestCase):

    def setUp(self):
        pass

    # stores and retrieve a tenant
    def test_key_creation(self):

        key_image_service = KeyImageService()
        data = {
            "study_id":"1.2.840.840.840.840.114350.2.358.2.2.2.2.2.2.1",
            "serie_name":"This is the name of the Series $ No more # 1234",
            "serie_id":"1.3.12.2.1107.5.1.4.1.1.1.1.1.1.1.1.1",
            "instance_id":"1.3.12.2.1107.5.1.4.2.2.2.2.2.2.2.2.2",
            "slice": 134,
            "wado_uri": "https://test.imexhs.com/wado?requestType=WADO&studyUID=1.2.840.840.840.840.114350.2.358.2.2.2.2.2.2.1&seriesUID=1.3.12.2.1107.5.1.4.1.1.1.1.1.1.1.1.1&objectUID=1.3.12.2.1107.5.1.4.2.2.2.2.2.2.2.2.2&contentType=image%2Fjpeg",
            "is_fusion":False,
            "backlayer":{},
            "is_multiframe": False,
            "patient_id":"1234567p",
            "n_studies": 1,
            "keyimage_id": "4A.11111111N"
        }
        key_image_service.store_keyimage(data)
        key_image_service.close()        

        # creates a new connection
        key_image_service.create_connection()
        ret_data = {
            "patient_id": "1234567p"
        }
        answer = key_image_service.retrieve_keyimages(ret_data)
        key_image_service.close()

        key_images = answer['key_images']
        # check response
        self.assertEqual(len(key_images), 1)
        self.assertEqual(key_images[0]['keyimageuid'], data['keyimage_id'])
        self.assertEqual(key_images[0]['patientid'], data['patient_id'])
        self.assertEqual(key_images[0]['slice'], data['slice'])
        self.assertEqual(key_images[0]['wadouri'], data['wado_uri'])


    # stores and retrieve a tenant
    def test_no_key(self):

        key_image_service = KeyImageService()
        ret_data = {
            "patient_id": "non_existent_12367"
        }
        answer = key_image_service.retrieve_keyimages(ret_data)
        key_image_service.close()
        key_images = answer['key_images']
        # check list is empty
        self.assertEqual(len(key_images), 0)


    # stores and retrieve a tenant
    def test_delete_key(self):

        key_image_service = KeyImageService()
        data = {
            "study_id":"1.2.840.840.840.840.114350.2.358.2.2.2.2.2.2.1",
            "serie_name":"This is the name of the Series $ No more # 1234",
            "serie_id":"1.3.12.2.1107.5.1.4.1.1.1.1.1.1.1.1.1",
            "instance_id":"1.3.12.2.1107.5.1.4.2.2.2.2.2.2.2.2.2",
            "slice": 134,
            "wado_uri": "https://test.imexhs.com/wado?requestType=WADO&studyUID=1.2.840.840.840.840.114350.2.358.2.2.2.2.2.2.1&seriesUID=1.3.12.2.1107.5.1.4.1.1.1.1.1.1.1.1.1&objectUID=1.3.12.2.1107.5.1.4.2.2.2.2.2.2.2.2.2&contentType=image%2Fjpeg",
            "is_fusion":False,
            "backlayer":{},
            "is_multiframe": False,
            "patient_id":"xyz1567p",
            "n_studies": 1,
            "keyimage_id": "KAU34M11111N"
        }
        key_image_service.store_keyimage(data)
        key_image_service.close()        

        # creates a new connection
        key_image_service.create_connection()
        key_image_service.delete_keyimage("KAU34M11111N")
        key_image_service.close()

        # creates a new connection
        key_image_service.create_connection()
        ret_data = {
            "patient_id": "xyz1567p"
        }
        answer = key_image_service.retrieve_keyimages(ret_data)
        key_image_service.close()
        key_images = answer['key_images']
        self.assertEqual(len(key_images), 0)
