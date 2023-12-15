// HydroScat emulator
//
// Tested on Arduino Uno R3
//
// Section 8.2 of HydroScat-6 user manual, revision J
//
// The HydroScat waits until it receives a carriage return, line feed, or other
// control character before responding to a command. It responds to every
// command, but does not echo characters when it receives them. If it receives a
// command it does not understand, it will echo the command followed by a question
// mark.
//
// The HydroScat’s responses usually start with an apostrophe (‘). Error
// messages start with an exclamation point, and primary data messages start with an
// asterisk (*).
//
// Commands are insensitive to case. They are shown below in upper case for
// clarity.
//
// Some commands accept arguments, which are separated from the base
// command, and from each other, by commas. Arguments may be individually
// omitted, in which case they will have no effect. For example, if a command
// accepts three arguments, in the form COMMAND,arg1,arg2,arg3, you may adjust
// only arg3 by entering COMMAND,,,arg3.

#include <stdlib.h>
#include "data.h"

#define MILLIS 1000
#define READ_SZ 80

void clear_buf(char *buf);
void serial_out(const char* buf, int length);
void read_input();
void gen_line();

bool echo;
bool transmit;
long start;
int row;

void setup() {
  echo = false;
  transmit = false;
  row = 0;

  start = millis();  

  // 8 data bits, 1 stop bit, no parity, hardware flow control
  Serial.begin(9600);
  while (!Serial);
}

void loop() {
  long now = millis();

  read_input();

  if (abs(now - start) >= MILLIS) {
    gen_line();
    start = now;
  }
}

void clear_buf(char* buf) {
  for (int i=0;i<READ_SZ;i++) buf[i] = '\0';
}

void serial_out(const char* buf, int length) {
  for (int i=0;i<length;i++) Serial.print(buf[i]);
}

void read_input() {
  static char buf[READ_SZ];
  static int i = 0;
  static int state = 0;
  
  if (Serial.available()) {
  
    bool eoln = false;
    
    char incoming_byte = Serial.read();

    // to uppercase
    if (incoming_byte >= 'a') incoming_byte -= ('a'-'A');

    // echo back to receiver
    if (echo) Serial.write(incoming_byte);

    if (i < READ_SZ) {
      if (incoming_byte == '\r') {
        // end of command
        if (echo) Serial.print(F("\r\n"));
        buf[i] = '\0';
        eoln = true;
      } else if (incoming_byte >= ' ') {
        // accumulate command (non-control) characters
        buf[i++] = incoming_byte;
      }
    } else {
      // Read up to max bytes allowed, otherwise abandon currently
      // accumulated "command" and reset state machine.
      i = 0;
      state = 0;
      transmit = false;
    }

    // Note: establishes general pattern; each state+command handler case should be a function; create/generate state diagram

    if (eoln) {
      if (state == 0 && strncmp(buf, "BURST,", 6) == 0 && strlen(buf) > 6) {
        // response is independent of argument after comma
        Serial.print(F("'Burst mode: 1 (ON)\r\n"));
        Serial.print(F("' Warmup time: 5 seconds\r\n"));
        Serial.print(F("' Burst duration: 15 seconds\r\n"));
        Serial.print(F("' Burst cycle: 10 minutes\r\n"));
        Serial.print(F("' Total duration: 0 hours (not in effect)\r\n"));
        Serial.print(F("'Sampling and Logging Parameters:\r\n"));
        Serial.print(F("' Log Period: 1 seconds\r\n"));
        Serial.print(F("' Start delay: 60 seconds\r\n"));
        Serial.print(F("' Sleep when memory full: 1\r\n"));
        Serial.print(F("' Start on power up: 0\r\n"));
      } else if (state == 0 && strncmp(buf, "DATE,", 5) == 0 && strlen(buf) > 5) {
        // instrument date not changed; just return the string
        Serial.print(F("'05/04/2023 22:35:42\r\n"));
      } else if (state == 0 && strncmp(buf, "FL,", 3) == 0 && strlen(buf) == 4) {
        // response is independent of argument after comma 
        Serial.print(F("'fl510\r\n"));
        Serial.print(F("' excitation: bb470\r\n"));
        Serial.print(F("' receiver: bb510\r\n"));
        Serial.print(F("' status: 1 (fl510 on, bb470 off)\r\n"));
        Serial.print(F("\r\n"));
        Serial.print(F("'fl671\r\n"));
        Serial.print(F("' excitation: bb442\r\n"));
        Serial.print(F("' receiver: bb671\r\n"));
        Serial.print(F("' status: 0 (fl671 on, bb671 off)\r\n"));
      } else if (strncmp(buf, "SLEEP", 5) == 0) {
        transmit = false;
        state = 0;
      } else if (state == 0 && strncmp(buf, "START,", 6) == 0 && strlen(buf) > 6) {
        // Empty string usually emitted before or after "Sampling starts...".
        Serial.print(F("\r\n"));
        unsigned int start_delay = buf[6]-'0';
        if (start_delay != 0) {
          Serial.print("'Sampling starts in 1 seconds.\r\n");
        }
        // Emitted after start and before data packets.
        // Reader will probably want to ignore it.
        Serial.print(F("'HS6\r\n"));
        row = 0;
        transmit = true;
        state = 1;
      } else if (state == 1 && strncmp(buf, "STOP", 4) == 0) {
        Serial.print(F("'Sampling stopped.\r\n"));
        transmit = false;
        state = 0;
      } else if (i > 0) {
        serial_out(buf, i);
        Serial.print(F("?\r\n"));
      }

      clear_buf(buf);
      i = 0;
    }
  }
}

// Note: output could be of two types: from data.h or dynamic based upon constraints

void gen_line() {
  char msg[80];

  // sprintf(msg, "** transmit: %d, state: %d, i: %d\r\n", transmit, state, i);
  // Serial.print(msg);

  if (transmit) {
    Serial.print(data[row]);
    Serial.print(F("\r\n"));

    row++;
    if (row == ROWS) row = 0;
  }
}