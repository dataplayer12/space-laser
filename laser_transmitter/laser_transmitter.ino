int x=0;
volatile bool enable=true;
void setup() {
  // put your setup code here, to run once:
pinMode(2,INPUT_PULLUP);
DDRD |= (1<<PD4);//pin number 4
DDRB |= (1<<PB0); //turn on bluetooth
PORTD |= (1<<PD4);//turn on debug led
PORTB |= (1<<PB0);
Serial.begin(9600);
attachInterrupt(digitalPinToInterrupt(2),turn_off,FALLING);
}

void loop() {
  // put your main code here, to run repeatedly:
if (enable){
if (Serial.available()){
  x=Serial.read();
}
}
else {
  Serial.end();
  PORTB &= ~(1<<PB0); //turn off bluetooth
  DDRD|=(1<<PD0);//make rx as output
  PORTD &= ~((1<<PD0)|(1<<PD4));//turn off laser
  //return;
}
}

void turn_off(){
//PORTD &= ~(1<<PD4);
//return; 
enable=false;
}

