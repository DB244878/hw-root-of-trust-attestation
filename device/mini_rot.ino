String firmware = "firmware_v2";
int svn = 2;

String deviceSecret = "device_secret_123";

String hashStr(String s) {
  long h = 0;
  for (int i = 0; i < s.length(); i++) {
    h = h * 31 + s[i];
  }
  return String(h);
}

String derive(String parent, String measurement) {
  return hashStr(parent + "|" + measurement);
}

String idev;
String ldev;
String runtime_id;

void boot_rom() {
  String firmware_measurement = hashStr(firmware);
  idev = derive(deviceSecret, firmware_measurement);

  String config_measurement = hashStr("config_v1");
  ldev = derive(idev, config_measurement);

  String runtime_measurement = hashStr("runtime_v1");
  runtime_id = derive(ldev, runtime_measurement);
}

void setup() {
  Serial.begin(9600);
  delay(2000);

  boot_rom();

  Serial.println("=== Mini Caliptra v2 ===");
  Serial.println("Device boot complete");
  Serial.println("Type: get_ids, measure, attest");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "get_ids") {
      Serial.println("IDEV=" + idev);
      Serial.println("LDEV=" + ldev);
      Serial.println("RT=" + runtime_id);
    }
    else if (cmd == "measure") {
      Serial.println("MEASURE=" + hashStr(firmware));
      Serial.println("SVN=" + String(svn));
    }
    else if (cmd == "attest") {
      String measurement = hashStr(firmware);
      String signature = hashStr(runtime_id + "|" + measurement + "|" + String(svn));

      Serial.println("ATTESTATION");
      Serial.println("MEASURE=" + measurement);
      Serial.println("SVN=" + String(svn));
      Serial.println("SIG=" + signature);
    }
    else {
      Serial.println("UNKNOWN_CMD");
    }
  }
}
