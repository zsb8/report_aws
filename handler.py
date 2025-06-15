import json
from src.utils.choose_graph_type import choose_graph_type as choose_graph_type
from src.utils.save_report_settings import save_report_settings as save_report_settings


def handler(event, context):
    """
    Lambda handler function
    """
    try:
        # Check if the path is /download_pdf
        path = event['requestContext']['http']['path']

        if path == "/choose_graph_type":
            print("Starting navigation to choose_graph_type function")
            body = json.loads(event['body'])
            csv_json = body.get('csv_json')
            graph_types = body.get('graph_types')
            if not csv_json:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing pdf_url'})
                }
            result, error = choose_graph_type(csv_json, graph_types)
            
            if error:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': error})
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Success',
                    'result': result
                })
            }

        if path == "/save_report_settings":
            print("Starting navigation to save_report_settings function")
            body = json.loads(event['body'])
            mydata = body.get('data')
            settings=json.dumps(mydata)
            if not settings:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing settings'})
                }
            result, error = save_report_settings(settings)
            
            if error:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': error})
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Success',
                    'result': result
                })
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 