#include<Wire.h>
//#define debug_mode

const int8_t MPUaddress=0x68; //I2C address of MPU-6050

int16_t acX=0;
int16_t acY=0;
int16_t acZ=0;

unsigned long sumacx=0;
unsigned long sumacy=0;
unsigned long sumacz=0;

int16_t acx_base=0;
int16_t acy_base=0;
int16_t acz_base=0;

int n_counts=0;
bool moved=false;

uint8_t gyro_settings=0x10;
//gyro_settings | measurement range
//    0x00      | +/- 250 deg/s
//    0x01      | +/- 500 deg/s
//    0x10      | +/- 1000deg/s
//    0x11      | +/- 2000deg/s

float divisor= (float) 131.0/pow(2,2);
int omega_threshold = 500;
int ac_threshold=10000;

int16_t driftX,driftY,driftZ;
float omegaX,omegaY,omegaZ;

const uint8_t notify_led = 7;
const uint8_t laser_switch = 13;

void setup() {
pinMode(notify_led,OUTPUT);
pinMode(laser_switch,OUTPUT);

#ifdef debug_mode
  Serial.begin(115200);
  while(!Serial) {}
  Serial.print("divisor=");
  Serial.println(divisor);
#endif

turn_off_laser();
delay(2000);
Wire.begin();

setupGyro();
//calibrateMPU();
setupAccel();

find_base_ac();
turn_on_laser();
}

void loop() {
  // put your main code here, to run repeatedly:
//readGyro();

readAccel();

find_if_moved();
if (moved) {
  #ifdef debug_mode
    Serial.println("Laser has moved!");
  #endif
  turn_off_laser();
  }

}

void turn_on_laser(){
  digitalWrite(laser_switch,HIGH);
  digitalWrite(notify_led,LOW);
  #ifdef debug_mode
    Serial.println("Turned on laser");
  #endif
}

void turn_off_laser(){
  digitalWrite(laser_switch,LOW);
  digitalWrite(notify_led,HIGH);
  #ifdef debug_mode
    Serial.println("Turned off laser");
  #endif
}

void setupAccel() {
  Wire.beginTransmission(MPUaddress);
  Wire.write(0x1C);
  Wire.write(0b00000000);
  Wire.endTransmission();
}

void readAccel() {
  Wire.beginTransmission(MPUaddress);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPUaddress,6,true);
  
  acX= Wire.read()<<8|Wire.read();
  acY= Wire.read()<<8|Wire.read();
  acZ= Wire.read()<<8|Wire.read();

}

void find_if_moved() {
//  moved |= (abs(omegaX)>=omega_threshold);
//  moved |= (abs(omegaY)>=omega_threshold);
//  moved |= (abs(omegaZ)>=omega_threshold);
//  moved |= (abs(acX-acx_base)>ac_threshold);
//  moved |= (abs(acY-acy_base)>ac_threshold);
  moved |= (abs(acZ-acz_base)>ac_threshold);
  #ifdef debug_mode
    Serial.print("acx= ");
    Serial.print(abs(acX));
    Serial.print(", acy= ");
    Serial.print(abs(acY));
    Serial.print(", acz= ");
    Serial.println(abs(acZ));
  #endif
}

void setupGyro() {
  Wire.beginTransmission(MPUaddress);
  Wire.write(0x6B);
  Wire.write(0b00001000); //Setting Bit 3 to 1 disables temp sensor
  Wire.endTransmission(true);
  Wire.beginTransmission(MPUaddress);
  Wire.write(0x1B); //Register to choose parameters of Gyro
  Wire.write(gyro_settings); 
  Wire.endTransmission();
  
}

void calibrateMPU() {
  /*The first few readings from the gyroscope after it is switched 
  on are unreliable. This function calibrates the gyroscope for 10 seconds
  (total 2500 readings) and averages them out to determine the drift 
  or noise present in the gyro. These drifts are subtracted from 
  all further readings of the gyro*/
  long gyroXsum =0;
  long gyroYsum =0;
  long gyroZsum =0;
#ifdef debug_mode 
Serial.print("Calibrating MPU.. Please wait\n");
#endif

for (int i=0; i<2500; i++) {
  Wire.beginTransmission(MPUaddress);
  Wire.write(0x43);
  Wire.endTransmission(false);
  Wire.requestFrom(MPUaddress,6,true);

int16_t  gyroXreading=Wire.read()<<8|Wire.read();
int16_t  gyroYreading=Wire.read()<<8|Wire.read();
int16_t  gyroZreading=Wire.read()<<8|Wire.read();

gyroXsum += gyroXreading;
gyroYsum += gyroYreading;
gyroZsum += gyroZreading;
delayMicroseconds(3200);

  }

int16_t driftX= int16_t(gyroXsum/2500.0);
int16_t driftY= int16_t(gyroYsum/2500.0);
int16_t driftZ= int16_t(gyroZsum/2500.0);

#ifdef debug_mode

  Serial.print("Calibration finished!\n");
  Serial.print("driftX= "); Serial.print(driftX);
  Serial.print("driftY= "); Serial.print(driftY);
  Serial.print("driftZ= "); Serial.println(driftZ);

#endif
}

void readGyro() {
  
  Wire.beginTransmission(MPUaddress);
  Wire.write(0x43);
  Wire.endTransmission(false);
  Wire.requestFrom(MPUaddress,6,true);
  
  int16_t  gyroXreading=(Wire.read()<<8|Wire.read())-driftX;
  int16_t  gyroYreading=(Wire.read()<<8|Wire.read())-driftY;
  int16_t  gyroZreading=(Wire.read()<<8|Wire.read())-driftZ;

  omegaX= (gyroXreading)/divisor;
  omegaY= (gyroYreading)/divisor;
  omegaZ= (gyroZreading)/divisor;

  #ifdef debug_mode
    Serial.print("omegaX= "); 
    Serial.print(omegaX);
    Serial.print(", omegaY= "); 
    Serial.print(omegaY);
    Serial.print(", omegaZ= "); 
    Serial.println(omegaZ);
  #endif
  }

void find_base_ac(){
  unsigned long start=millis();

  while(millis()-start<250) {
    readAccel();
    sumacx+=acX;
    sumacy+=acY;
    sumacz+=acZ;
    n_counts+=1;
}

acx_base=sumacx/n_counts;
acy_base=sumacy/n_counts;
acz_base=sumacz/n_counts;

#ifdef debug_mode

  Serial.print("acx,y,z = ");
  Serial.print(acx_base);
  Serial.print(", ");
  Serial.print(acy_base);
  Serial.print(", ");
  Serial.println(acz_base);

#endif
}
