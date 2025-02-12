/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp32-cam-post-image-photo-server/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

#include <Arduino.h>
#include <WiFi.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_camera.h"

#include "SD_MMC.h"

String DEVICE_UUID;
String WIFI_SSID;
String WIFI_PASSWORD;

String textoProcurado = "DEVICE_UUID";
String textoProcurado1 = "WIFI_SSID";
String textoProcurado2 = "WIFI_PASSWORD";

// String serverName = "192.168.1.32";  // REPLACE WITH YOUR SERVER IP ADDRESS
String serverName = "marcosvianadev.ddns.net";  //OR REPLACE WITH YOUR DOMAIN NAME

String serverPath = "/api/upload/";  // The default serverPath should be upload.php

const int serverPort = 3199;
const int images = 50;                // How much images captures per period
const int images_fast_time = 30000;   //30 seconds
const int images_slow_time = 180000;  // 3 minutes
int total_images = 0;

WiFiClient client;

// CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

#define LED_BUILTIN 4
#define FLASH_LED 33

int timerInterval = images_fast_time / images;  // time between each HTTP POST image
unsigned long previousMillis = 0;               // last time image was sent

void initSDCard() {
  if (!SD_MMC.begin()) {
    Serial.println("Card Mount Failed");
    ESP.restart();
  }
  uint8_t cardType = SD_MMC.cardType();

  if (cardType == CARD_NONE) {
    Serial.println("No SD card attached");
    ESP.restart();
  }

  Serial.print("SD Card Type: ");
  if (cardType == CARD_MMC) {
    Serial.println("MMC");
  } else if (cardType == CARD_SD) {
    Serial.println("SDSC");
  } else if (cardType == CARD_SDHC) {
    Serial.println("SDHC");
  } else {
    Serial.println("UNKNOWN");
  }
  uint64_t cardSize = SD_MMC.cardSize() / (1024 * 1024);
  Serial.printf("SD Card Size: %lluMB\n", cardSize);
}

void readConfig() {
  File file = SD_MMC.open("/esp32.txt", FILE_READ);
  if (!file) {
    Serial.println("Opening file to read failed");
    ESP.restart();
    return;
  }
  Serial.println("Loading config file...");
  while (file.available()) {
    String linha = file.readStringUntil('\n');
    if (linha.startsWith(textoProcurado)) {
      DEVICE_UUID = linha.substring(textoProcurado.length() + 1);
    } else if (linha.startsWith(textoProcurado1)) {
      WIFI_SSID = linha.substring(textoProcurado1.length() + 1);
    } else if (linha.startsWith(textoProcurado2)) {
      WIFI_PASSWORD = linha.substring(textoProcurado2.length() + 1);
    }
  }
  file.close();
  Serial.println("Configs loaded.");
  Serial.println("DEVICE_UUID: " + DEVICE_UUID);
  Serial.println("WIFI_SSID: " + WIFI_SSID);
  Serial.println("WIFI_PASSWORD: " + WIFI_PASSWORD);
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // Set the pin as output CAM LED (FLASH)
  pinMode(33, OUTPUT);           // Set the pin as output INTERNAL LED (red dot)
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  Serial.begin(115200);
  initSDCard();
  readConfig();

  WiFi.mode(WIFI_STA);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(50);
  }
  Serial.println();
  Serial.print("ESP32-CAM IP Address: ");
  Serial.println(WiFi.localIP());

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // init with high specs to pre-allocate larger buffers
  if (psramFound()) {
    // FRAMESIZE_QVGA (320 x 240)
    // FRAMESIZE_CIF (352 x 288)
    // FRAMESIZE_VGA (640 x 480)
    // FRAMESIZE_SVGA (800 x 600)
    // FRAMESIZE_XGA (1024 x 768)
    // FRAMESIZE_SXGA (1280 x 1024)
    // FRAMESIZE_UXGA (1600 x 1200)
    config.frame_size = FRAMESIZE_XGA;  // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    config.jpeg_quality = 10;           //0-63 lower number means higher quality
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 18;  //0-63 lower number means higher quality
    config.fb_count = 1;
  }

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    delay(1000);
    ESP.restart();
  }
  sendPhoto();
}

void loop() {
  unsigned long currentMillis = millis();
  if (total_images > images) {
    timerInterval = images_slow_time / images;
  }
  if (currentMillis - previousMillis >= timerInterval) {
    sendPhoto();
    previousMillis = currentMillis;
  }
  if (total_images >= images + images) {
    Serial.print("Reach maximum files...");
    esp_deep_sleep_start();
  }
}

String sendPhoto() {
  digitalWrite(FLASH_LED, LOW);    //Turn on
  digitalWrite(LED_BUILTIN, LOW);  //Turn on
  String getAll;
  String getBody;

  camera_fb_t *fb = NULL;
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    delay(1000);
    ESP.restart();
  }

  Serial.println("Connecting to file server: " + serverName);

  if (client.connect(serverName.c_str(), serverPort)) {
    Serial.println("Connection successful!");
    String head = "--???\r\nContent-Disposition: form-data; name=\"imageFile\"; filename=\"esp32-cam.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String tail = "\r\n--???--\r\n";

    uint32_t imageLen = fb->len;
    uint32_t extraLen = head.length() + tail.length();
    uint32_t totalLen = imageLen + extraLen;

    client.println("POST " + serverPath + " HTTP/1.1");
    client.println("Host: " + serverName);
    client.println("Content-Length: " + String(totalLen));
    client.println("Content-Type: multipart/form-data; boundary=???;");
    client.println("Device-UUID: " + String(DEVICE_UUID));
    client.println();
    client.print(head);

    uint8_t *fbBuf = fb->buf;
    size_t fbLen = fb->len;
    for (size_t n = 0; n < fbLen; n = n + 1024) {
      if (n + 1024 < fbLen) {
        client.write(fbBuf, 1024);
        fbBuf += 1024;
      } else if (fbLen % 1024 > 0) {
        size_t remainder = fbLen % 1024;
        client.write(fbBuf, remainder);
      }
    }
    client.print(tail);

    esp_camera_fb_return(fb);

    int timoutTimer = 10000;
    long startTimer = millis();
    boolean state = false;

    while ((startTimer + timoutTimer) > millis()) {
      Serial.print(".");
      delay(100);
      while (client.available()) {
        char c = client.read();
        if (c == '\n') {
          if (getAll.length() == 0) { state = true; }
          getAll = "";
        } else if (c != '\r') {
          getAll += String(c);
        }
        if (state == true) { getBody += String(c); }
        startTimer = millis();
      }
      if (getBody.length() > 0) { break; }
    }
    Serial.println();
    client.stop();
    Serial.println(getBody);
  } else {
    getBody = "Connection to " + serverName + " failed.";
    Serial.println(getBody);
  }
  total_images += 1;
  Serial.println(total_images);
  digitalWrite(LED_BUILTIN, HIGH);  //Turn off
  digitalWrite(FLASH_LED, HIGH);    //Turn off
  return getBody;
}