import base64
import traceback
from http import HTTPStatus

from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from aws_lambda_powertools.event_handler.exceptions import (InternalServerError)
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.common.handler import JunctionNetEventHandler


handler = JunctionNetEventHandler('Muestras')
app_service = handler.service_factory.build()

cors_config = CORSConfig(allow_origin=handler.env_vars.CORS_ALLOW_ORIGIN, max_age=300)
app = APIGatewayRestResolver(cors=cors_config)


@app.post("/upload")
def upload():
    body = app.current_event.body

    if app.current_event.get('isBase64Encoded', False):
        body = base64.b64decode(body).decode('latin-1', errors='ignore')

    boundary = app.current_event['headers']['content-type'].split("boundary=")[1]
    boundary = f"--{boundary}"
    filedata = app_service.csv_document.parse_multipart_formdata(body, boundary)
    try:
        response = app_service.upload(filedata.get("file_content"), filedata.get("filename"))
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, content_type="application/json", body=handler.response_with.toast_message(message=f"Error Uploading: {e}", type="error", title="Error", show_toast=True))


    try:
        app_service.import_data(response.get("local_path"))
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, content_type="application/json", body=handler.response_with.toast_message(message=f"Error Importing: {e}", type="error", title="Error", show_toast=True))

    # metrics.add_metric(name="CreatedResults", unit=MetricUnit.Count, value=1, resolution=MetricResolution.High)
    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.plain_body(response))


@app.get("/user/muestras")
def find_all():
    print("find_all...")
    try:
        response = app_service.find_user_data(serialize=True)
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        raise InternalServerError(f"ERROR: {e}") from e


    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.plain_body(response))


@app.get("/muestras")
def find_all_muestras():
    print("find_all...")
    try:
        response = app_service.find_user_data(serialize=True)
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        raise InternalServerError(f"ERROR: {e}") from e


    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.plain_body(response))


@app.get("/muestrassz-estas")
def muestrassz_estas():

    try:
        response = app_service.find_user_data(serialize=True)
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        raise InternalServerError(f"ERROR: {e}") from e

    print(response)
    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.plain_body(response))


@app.get("/user/muestra")
def find_muestra():
    muestra_id = app.current_event.get_query_string_value("muestra_id")
    print(f"find_muestra: {muestra_id}")
    try:
        response = app_service.find_muestra(muestra_id, serialize=True)

        # print("Exporting muestra")
        # export_excel(app_service, response)
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        raise InternalServerError(f"ERROR: {e}") from e

    print(response)
    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.plain_body(response))


@app.get("/muestra")
def get_muestra():
    muestra_id = app.current_event.get_query_string_value("muestra_id")
    print(f"find_muestra: {muestra_id}")
    try:
        response = app_service.find_muestra(muestra_id, serialize=True)
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        raise InternalServerError(f"ERROR: {e}") from e

    print(response)
    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.plain_body(response))



@app.delete("/user/muestra")
def delete_muestra():
    muestra_id = app.current_event.get_query_string_value("muestra_id")
    print(f"find_muestra: {muestra_id}")
    try:
        app_service.delete_muestra(muestra_id)
    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, content_type="application/json",body=handler.response_with.toast_message(f"ERROR: {e}"))


    return Response(status_code=HTTPStatus.OK.value, content_type="application/json",
                    body=handler.response_with.toast_message("Muestra eliminada"))


@app_service.logger.inject_lambda_context(log_event=handler.env_vars.LOG_EVENT)
@app_service.metrics.log_metrics(capture_cold_start_metric=True)
def proxy_handler(event, context: LambdaContext):
    handler.event = event
    handler.print_event_details()

    handler.init_metrics(app_service.metrics)
    # handler.response_with.init_tracer(app_service.tracer)
    handler.init_logger(app_service.logger)

    app_service.context = handler.get_user_context()

    response = app.resolve(event, context)

    return response
