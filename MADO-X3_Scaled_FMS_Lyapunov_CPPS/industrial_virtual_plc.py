import asyncio
import json
import logging
from asyncua import Server, ua
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

incoming_telemetry = {}

def on_mqtt_message(client, userdata, msg):
    global incoming_telemetry
    try:
        incoming_telemetry = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        logging.error(f"[MQTT PARSE ERROR] {e}")

async def main():
    global incoming_telemetry

    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840/freeopcua/server/")
    server.set_server_name("MADO_X3_Virtual_Siemens_S7_1500")

    uri = "http://mado-x3.industry50.org/plc/"
    idx = await server.register_namespace(uri)

    objects = server.nodes.objects
    db100 = await objects.add_folder(idx, "DB100_MADO_X3_Gigafactory_Telemetry")

    # Station Registers mapped 1:1 to AnyLogic telemetry JSON keys (including true sink count & model time)
    reg_model_hours = await db100.add_variable(idx, "model_hours", 0.0, ua.VariantType.Double)
    reg_sink_count = await db100.add_variable(idx, "sink_count", 0, ua.VariantType.Int64)
    reg_q_acc = await db100.add_variable(idx, "q_accumulation", 0, ua.VariantType.Int32)
    reg_q_staging = await db100.add_variable(idx, "q_staging", 0, ua.VariantType.Int32)
    reg_q_down = await db100.add_variable(idx, "q_downstream", 0, ua.VariantType.Int32)
    reg_q_insp = await db100.add_variable(idx, "q_inspection", 0, ua.VariantType.Int32)
    reg_q_pack = await db100.add_variable(idx, "q_packaging", 0, ua.VariantType.Int32)
    reg_q_pal = await db100.add_variable(idx, "q_palletizer", 0, ua.VariantType.Int32)
    reg_power = await db100.add_variable(idx, "power_kw", 14.4, ua.VariantType.Double)

    # Actuation Control Registers
    reg_speed_boost = await db100.add_variable(idx, "speed_boost", False, ua.VariantType.Boolean)
    reg_gate_cluster_a = await db100.add_variable(idx, "gate_cluster_A", False, ua.VariantType.Boolean)
    reg_gate_cluster_b = await db100.add_variable(idx, "gate_cluster_B", False, ua.VariantType.Boolean)
    reg_reset_nominal = await db100.add_variable(idx, "reset_nominal", True, ua.VariantType.Boolean)

    for node in [reg_model_hours, reg_sink_count, reg_q_acc, reg_q_staging, reg_q_down, reg_q_insp, reg_q_pack, reg_q_pal, reg_power, reg_speed_boost, reg_gate_cluster_a, reg_gate_cluster_b, reg_reset_nominal]:
        await node.set_writable()

    mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id="MADO_X3_PLC_Gateway")
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.connect("localhost", 1883, keepalive=60)
    mqtt_client.subscribe("factory/telemetry/scaled_state")
    mqtt_client.loop_start()

    logging.info("[PLC SERVER] MADO-X3 Virtual Siemens S7-1500 PLC Running at opc.tcp://127.0.0.1:4840")

    async with server:
        while True:
            if incoming_telemetry:
                try:
                    await reg_model_hours.write_value(ua.DataValue(ua.Variant(float(incoming_telemetry.get("model_hours", 0.0)), ua.VariantType.Double)))
                    await reg_sink_count.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("sink_count", 0)), ua.VariantType.Int64)))
                    await reg_q_acc.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("q_accumulation", 0)), ua.VariantType.Int32)))
                    await reg_q_staging.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("q_staging", 0)), ua.VariantType.Int32)))
                    await reg_q_down.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("q_downstream", 0)), ua.VariantType.Int32)))
                    await reg_q_insp.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("q_inspection", 0)), ua.VariantType.Int32)))
                    await reg_q_pack.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("q_packaging", 0)), ua.VariantType.Int32)))
                    await reg_q_pal.write_value(ua.DataValue(ua.Variant(int(incoming_telemetry.get("q_palletizer", 0)), ua.VariantType.Int32)))
                    await reg_power.write_value(ua.DataValue(ua.Variant(float(incoming_telemetry.get("power_kw", 14.4)), ua.VariantType.Double)))
                except Exception as sync_err:
                    logging.error(f"[PLC SYNC ERROR] {sync_err}")
                incoming_telemetry = {}

            await asyncio.sleep(0.05)

if __name__ == "__main__":
    logging.getLogger("asyncua").setLevel(logging.ERROR)
    asyncio.run(main())