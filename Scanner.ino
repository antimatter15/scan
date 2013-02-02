/*
	This is the code which goes on the Arduino.
	It's really simple, all it does is to broadcast
	whenever the state of the little aluminum foil
	contact changes over the serial.
*/
void setup() {
	// initialize serial communication at 9600 bits per second:
	Serial.begin(9600);
}

// We do some crude input filtering so so that
// weird values don't do weird things
float lastValue = 1.0;
int lastState = 1;

// the loop routine runs over and over again forever:
void loop() {
	// read the input on analog pin 0:
	int sensorValue = digitalRead(A0);
	// weighted average of 90% previous state, 10% new state
	lastValue = lastValue * 0.9 + (float) sensorValue * 0.1;
	int newState = lastState;
	
	if(lastValue > 0.99){ // change state at this level
		newState = 1;
	}else if(lastValue < 0.01){ // change state at this other level
		newState = 0;
	}
	// if the state transition is from 0 to 1, means lid closed
	if(newState == 1 && lastState == 0){
		Serial.println("Lid closed");
	}
	lastState = newState;
	// delay, because delays are cool, right?
	delay(10);
}
