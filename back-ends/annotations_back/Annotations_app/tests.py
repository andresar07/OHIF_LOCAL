from django.test import TestCase

from Annotations_app.services.annotations_services import AnnotationsService


class AnnotationsTestCase(TestCase):

    def setUp(self):
        pass

    def test_version_creation(self):

        annotation_service = AnnotationsService()    
        user_id = 'default_user'
        study_id = "1.2.840.113704.1.111.7500.1524746113.1"

        data_version = annotation_service.create_version(study_id, user_id)
        annotation_service.close()

        self.assertTrue(data_version)
        self.assertGreater(data_version, 0)


    def test_get_all_versions(self):

        annotation_service = AnnotationsService()
        study_id = "1.2.840.113704.1.111.7500.1524746113.1"
        user_id = 'default_user'

        list_versions = annotation_service.get_all_versions(study_id)
        annotation_service.commit()
        annotation_service.close()

        annotation_service.create_connection()
        annotation_service.create_version(study_id, user_id)
        annotation_service.commit()
        annotation_service.close()

        annotation_service.create_connection()
        current_version = annotation_service.get_all_versions(study_id)
        annotation_service.commit()
        annotation_service.close()


        self.assertEqual(len(list_versions), 0)
        self.assertEqual(len(current_version), 1)


    def test_save_annotations(self):
        
        annotation_service = AnnotationsService()
        user_id = 'default_user'
        study_id = "1.2.4.0.13.1.4.2252867.20230827044325015.1"

        data = [
                {
                "studyUid": "1.2.4.0.13.1.4.2252867.20230827044325015.1",
                "seriesUid": "1.2.156.14702.3.696.2.20230827045627519.832",
                "instanceUid": "1.2.156.14702.3.696.3.20230827045628669.943",
                "modality": "MR",
                "annotationTitle": "none",
                "annotationType": "LINE",
                "data": [
                    [
                        105.25335821068222,
                        "mm",
                        "length"
                    ]
                ],
                "annotationParameters": [
                    154.73684210526315,
                    160.74955340811553,
                    155.26315789473682,
                    303.20569333158153
                ],
                "slice": "18/35",
                "annotationCreatedBy": "",
                "_id": 5
            },
        ]

        version = annotation_service.create_version(study_id, user_id)

        annotation_saved = annotation_service.save_annotations(data, user_id, version)
        
        annotation_service.commit()
        annotation_service.close()

        self.assertTrue(annotation_saved)


    def test_get_annotations(self):
        
        annotation_service = AnnotationsService()
        user_id = 'default_user'
        study_id = "1.2.4.0.13.1.4.2252867.20230827044325015.1"
        data = [
                {
                "studyUid": "1.2.4.0.13.1.4.2252867.20230827044325015.1",
                "seriesUid": "1.2.156.14702.3.696.2.20230827045627519.832",
                "instanceUid": "1.2.156.14702.3.696.3.20230827045628669.943",
                "modality": "MR",
                "annotationTitle": "none",
                "annotationType": "LINE",
                "data": [
                    [
                        105.25335821068222,
                        "mm",
                        "length"
                    ]
                ],
                "annotationParameters": [
                    154.73684210526315,
                    160.74955340811553,
                    155.26315789473682,
                    303.20569333158153
                ],
                "slice": "18/35",
                "annotationCreatedBy": "",
                "_id": 5
            },
        ]

        version = annotation_service.create_version(study_id, user_id)
        annotation_saved = annotation_service.save_annotations(data, user_id, version)
        annotation_service.commit()
        annotation_service.close()


        annotation_service.create_connection()
        list_versions = annotation_service.get_all_versions(study_id)
        annotations = annotation_service.get_annotations(study_id, list_versions)
        annotation_service.commit()
        annotation_service.close()

        self.assertTrue(annotation_saved)
        self.assertTrue(annotations)


        
