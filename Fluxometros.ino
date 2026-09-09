
#define fluxometro1 3
#define fluxometro2 5
#define fluxometro3 6
#define fluxometro4 9

String recebido; //Valores fixados
float fluxo1;
float fluxo2;
float fluxo3;
float fluxo4;
float vfluxo1 = 0;
float vfluxo2 = 0;
float vfluxo3 = 0;
float vfluxo4 = 0;
 
int i = 0;

void setup() 
{
    pinMode(fluxometro1, OUTPUT);
    pinMode(fluxometro2, OUTPUT);
    pinMode(fluxometro3, OUTPUT);
    pinMode(fluxometro4, OUTPUT);
    Serial.begin(9600);
    pinMode(0,OUTPUT);
}

void fluxo() 
{
    vfluxo1 = ((fluxo1)/5)*1024;
    vfluxo2 = ((fluxo2)/5)*1024;
    vfluxo3 = ((fluxo3)/5)*1024;
    vfluxo4 = ((fluxo4)/5)*1024;
    
    analogWrite(fluxometro1, map(vfluxo1,0,1023,0,255));
    analogWrite(fluxometro2, map(vfluxo2,0,1023,0,255));
    analogWrite(fluxometro3, map(vfluxo3,0,1023,0,255));
    analogWrite(fluxometro4, map(vfluxo4,0,1023,0,255));
     
    Serial.print("Fluxômetro 1: ");
    Serial.print(fluxo1);
    Serial.print(", Fluxômetro 2: ");
    Serial.print(fluxo2);
    Serial.print(", Fluxômetro 3: ");
    Serial.print(fluxo3);
    Serial.print(", Fluxômetro 4: ");
    Serial.println(fluxo4);
}

void loop() {
  i = 0;

  if (Serial.available() > 0) {
    recebido = Serial.readStringUntil('\n');
    if (recebido.startsWith("f1 = ")){
      recebido.remove(0,5);
      fluxo1 = recebido.toFloat();
      fluxo();  
    }

    if (recebido.startsWith("f2 = ")){
      recebido.remove(0,5);
      fluxo2 = recebido.toFloat();
      fluxo();
    }

    if (recebido.startsWith("f3 = ")){
      recebido.remove(0,5);
      fluxo3 = recebido.toFloat();
      fluxo();
    }

    if (recebido.startsWith("f4 = ")){
      recebido.remove(0,5);
      fluxo4 = recebido.toFloat();
      fluxo();
    }
     if (recebido == "scan"){
      //recebido.remove(0,5);
      i = 1;
      digitalWrite(i,HIGH);
    }
  }
 }
