#include <mqtt/async_client.h>
#include <string>
#include <iostream>
#include <chrono>
#include <thread>
#include <limits>

// On Debian/Raspberry Pi: sudo apt-get install libpaho-mqttpp3-dev libpaho-mqtt1.3 libpaho-mqtt-dev

class mqtt_handler : public virtual mqtt::callback {
public:
    // Connection settings
    std::string broker_address = "tcp://localhost:1883"; // Replace with your broker address
    std::string client_id = "cpp_mqtt_handler";          // You can customize this
    int qos = 1;

    double base_target = std::numeric_limits<double>::quiet_NaN();
    double base_vel    = std::numeric_limits<double>::quiet_NaN();
    double shoulder_target = std::numeric_limits<double>::quiet_NaN();
    double shoulder_vel    = std::numeric_limits<double>::quiet_NaN();
    double elbow_target = std::numeric_limits<double>::quiet_NaN();
    double elbow_vel    = std::numeric_limits<double>::quiet_NaN();
    double wrist_target = std::numeric_limits<double>::quiet_NaN();
    double wrist_vel    = std::numeric_limits<double>::quiet_NaN();
    bool gripper_open = false;
    bool waiting_for_button = true;

    mqtt_handler() : client_(broker_address, client_id)
    {
        client_.set_callback(*this);

        mqtt::connect_options connOpts;
        connOpts.set_clean_session(true);

        connect_with_retry(connOpts);

        // Subscriptions (retain parity with Python)
        subscribe("target/base");
        subscribe("target/elbow");
        subscribe("target/shoulder");
        subscribe("target/wrist");
        subscribe("waiting_for_button");
        subscribe("gripper");
    }

    ~mqtt_handler() {
        try {
            disconnect();
        } catch (...) {
            // swallow exceptions during destruction
        }
    }

    void publish(const std::string& topic, const std::string& msg) {
        auto pubmsg = mqtt::make_message(topic, msg);
        pubmsg->set_qos(qos);
        pubmsg->set_retained(true); // parity with Python retain=True
        client_.publish(pubmsg);
    }

    void disconnect() {
        try {
            if (client_.is_connected()) {
                std::cout << "Disconnecting from MQTT..." << std::endl;
                client_.disconnect()->wait();
            }
        } catch (const std::exception& e) {
            std::cerr << "Error disconnecting: " << e.what() << std::endl;
        }
    }

    void subscribe(const std::string& topic) {
        try {
            client_.subscribe(topic, qos)->wait();
            std::cout << "Subscribed to '" << topic << "'" << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "Subscribe failed for '" << topic << "': " << e.what() << std::endl;
        }
    }

    // mqtt::callback overrides
    void connection_lost(const std::string& cause) override {
        std::cerr << "Connection lost: " << cause << std::endl;

        // Attempt to reconnect loop
        mqtt::connect_options connOpts;
        connOpts.set_clean_session(true);
        connect_with_retry(connOpts);

        // Re-subscribe after reconnect
        subscribe("target/base");
        subscribe("target/elbow");
        subscribe("target/shoulder");
        subscribe("target/wrist");
        subscribe("waiting_for_button");
        subscribe("gripper");
    }

    void message_arrived(mqtt::const_message_ptr msg) override {
        const std::string topic = msg->get_topic();
        const std::string payload = msg->to_string();
        // std::cout << "[MQTT] Received on '" << topic << "': " << payload << std::endl;

        if (topic == "target/base") {
            parse_two_numbers(payload, base_target, base_vel);
        } else if (topic == "target/shoulder") {
            parse_two_numbers(payload, shoulder_target, shoulder_vel);
        } else if (topic == "target/elbow") {
            parse_two_numbers(payload, elbow_target, elbow_vel);
        } else if (topic == "target/wrist") {
            parse_two_numbers(payload, wrist_target, wrist_vel);
        } else if (topic == "gripper") {
            gripper_open = (payload == "open");
        } else if (topic == "waiting_for_button") {
            waiting_for_button = (payload == "true");
        }
    }

    void delivery_complete(mqtt::delivery_token_ptr) override {
        // No-op
    }

private:
    mqtt::async_client client_;

    static void parse_two_numbers(const std::string& payload, double& a, double& b) {
        auto pos = payload.find(';');
        if (pos == std::string::npos) return;
        try {
            a = std::stod(payload.substr(0, pos));
            b = std::stod(payload.substr(pos + 1));
        } catch (...) {
            // ignore parse errors
        }
    }

    void connect_with_retry(const mqtt::connect_options& connOpts) {
        const int max_attempts = 10;
        int attempt = 0;
        while (true) {
            try {
                client_.connect(connOpts)->wait();
                return;
            } catch (const std::exception& e) {
                if (++attempt >= max_attempts) {
                    std::cerr << "Failed to connect to MQTT broker after " << attempt << " attempts: " << e.what() << std::endl;
                    throw;
                }
                std::cerr << "Connect attempt " << attempt << " failed: " << e.what() << ". Retrying in 1s..." << std::endl;
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }
        }
    }
};

// Optional tiny demo: Define MQTT_STANDALONE_DEMO to test publish loop.
// int main() {
//     mqtt_handler handler;
//     double i = 20.0;
//     while (true) {
//         i -= 0.5;
//         handler.publish("base", std::to_string(i));
//         std::this_thread::sleep_for(std::chrono::milliseconds(50));
//     }
//     return 0;
// }
