import traceback
from aws_lambda_powertools.utilities.data_classes import event_source, EventBridgeEvent
from src.domain.exports import export_excel
from src.common.handler import JunctionNetEventHandler

jnet = JunctionNetEventHandler('Muestras')
app_service = jnet.service_factory.build()


@app_service.logger.inject_lambda_context(log_event=True)
@app_service.metrics.log_metrics(capture_cold_start_metric=True)
@event_source(data_class=EventBridgeEvent)
def lambda_handler(event: EventBridgeEvent, context):
    jnet.event = event
    data = event.detail
    print(f"EVENTIRRIX received: {event}")

    jnet.print_event_details()

    jnet.init_metrics(app_service.metrics)
    # jnet.init_tracer(app_service.tracer)
    jnet.init_logger(app_service.logger)

    print("#" * 88)
    print(f"EXPORT Event: {event}")
    print(f"Data: {data}")
    print("#" * 88)
    print("$" * 88)
    print("&" * 88)

    app_service.context = data
    muestra_id = data.get('muestra_id')
    print(f"find_muestra: {muestra_id}")
    try:
        response = app_service.find_muestra(muestra_id, serialize=True)
        print("Exporting muestra")
        excel_buffer = export_excel(response)

        # Generate file name with timestamp
        file_name = f"{muestra_id}/indices.xlsx"

        upload_response = app_service.s3_repository.upload(file_name, excel_buffer)  # Upload the file

        return upload_response

    except Exception as e:
        print(traceback.format_exc())
        app_service.logger.exception(e)
        traceback.print_exc()
        raise Exception
