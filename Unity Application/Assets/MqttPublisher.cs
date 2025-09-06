using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Client.Options;
using System.Threading.Tasks;
using MQTTnet.Client.Receiving;

public class MqttPublisher : MonoBehaviour
{
    MqttFactory factory;
    IMqttClient mqttClient = null;
    bool connected = false;
    MqttReceiver receiver;

    public void Start()
    {
        receiver = GetComponent<MqttReceiver>();
        factory = new MqttFactory();
        mqttClient = factory.CreateMqttClient();

        // Attach the message received handler
        mqttClient.ApplicationMessageReceivedHandler = new MqttApplicationMessageReceivedHandlerDelegate(e =>
        {
            string topic = e.ApplicationMessage.Topic;
            string payload = System.Text.Encoding.UTF8.GetString(e.ApplicationMessage.Payload);
            receiver.ReceiveMessage(topic, payload);
        });


        _ = Connect();
    }

    public void SendHi()
    {
        Send("target", "0;0;0;0");
    }

    async Task Connect()
    {
        var options = new MqttClientOptionsBuilder()
            .WithTcpServer("10.0.0.251", 1883)
            .Build();

        await mqttClient.ConnectAsync(options);
        connected = true;

        // Subscribe to a topic after connecting
        await mqttClient.SubscribeAsync("position/base"); 
        await mqttClient.SubscribeAsync("position/shoulder"); 
        await mqttClient.SubscribeAsync("position/elbow"); 
        await mqttClient.SubscribeAsync("position/wrist"); 
        await mqttClient.SubscribeAsync("button"); 
        //Debug.Log("[MQTT] Subscribed to topic 'tester2/whatsup'");
    }

    public void Send(string topic, string msg)
    {
        _ = DoSend(topic, msg);
    }

    [SerializeField] string topic;
    [SerializeField] string msg;
    public void SendAngle() {
        Send(topic, msg.ToString());
    }

    async Task DoSend(string topic, string msg)
    {
        if (!connected)
        {
            //Debug.Log("Not connected yet.");
            await Task.Delay(100);
        }
        var message = new MqttApplicationMessageBuilder()
            .WithTopic(topic)
            .WithPayload(msg)
            .WithExactlyOnceQoS()
            .WithRetainFlag(false)
            .Build();

        await mqttClient.PublishAsync(message);
        //Debug.Log($"[MQTT] Message published to {message.Topic}: {msg}");
    }

    private void OnDisable()
    {
        if (mqttClient != null && mqttClient.IsConnected)
        {
            _ = mqttClient.DisconnectAsync();
        }
    }
}
