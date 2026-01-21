// --- CÓDIGO FINAL: 4 SEMÁFOROS SINCRONIZADOS (PARES) ---

// Semáforo 1 (Norte)
const int S1_R = 13; const int S1_A = 12; const int S1_V = 11;
// Semáforo 2 (Este)
const int S2_R = 10; const int S2_A = 9;  const int S2_V = 8;
// Semáforo 3 (Sur) - Se mueve igual que el 1
const int S3_R = 7;  const int S3_A = 6;  const int S3_V = 5;
// Semáforo 4 (Oeste) - Se mueve igual que el 2
const int S4_R = 4;  const int S4_A = 3;  const int S4_V = 2;

char fase;

void setup() {
  // Configurar pines 2 al 13
  for (int i = 2; i <= 13; i++) { pinMode(i, OUTPUT); }
  Serial.begin(9600);
  todoRojo();
}

void loop() {
  if (Serial.available() > 0) {
    fase = Serial.read();
    cambiarFase(fase);
  }
}

void todoRojo() {
  // Pone TODOS en Rojo (Seguridad)
  digitalWrite(S1_V, 0); digitalWrite(S1_A, 0); digitalWrite(S1_R, 1);
  digitalWrite(S2_V, 0); digitalWrite(S2_A, 0); digitalWrite(S2_R, 1);
  digitalWrite(S3_V, 0); digitalWrite(S3_A, 0); digitalWrite(S3_R, 1);
  digitalWrite(S4_V, 0); digitalWrite(S4_A, 0); digitalWrite(S4_R, 1);
}

void cambiarFase(char f) {
  // Limpiamos luces anteriores (apagamos verdes y amarillos)
  digitalWrite(S1_V, 0); digitalWrite(S1_A, 0);
  digitalWrite(S2_V, 0); digitalWrite(S2_A, 0);
  digitalWrite(S3_V, 0); digitalWrite(S3_A, 0);
  digitalWrite(S4_V, 0); digitalWrite(S4_A, 0);
  
  // Aseguramos rojos base
  digitalWrite(S1_R, 1); digitalWrite(S2_R, 1); digitalWrite(S3_R, 1); digitalWrite(S4_R, 1);

  // --- LÓGICA DE PARES ---

  // 'V' -> VERTICAL VERDE (S1 y S3 Avanzan)
  if (f == 'V') {
    digitalWrite(S1_R, 0); digitalWrite(S1_V, 1); // S1 Verde
    digitalWrite(S3_R, 0); digitalWrite(S3_V, 1); // S3 Verde
  }

  // 'v' -> VERTICAL AMARILLO
  if (f == 'v') {
    digitalWrite(S1_R, 0); digitalWrite(S1_A, 1); // S1 Amarillo
    digitalWrite(S3_R, 0); digitalWrite(S3_A, 1); // S3 Amarillo
  }

  // 'H' -> HORIZONTAL VERDE (S2 y S4 Avanzan)
  if (f == 'H') {
    digitalWrite(S2_R, 0); digitalWrite(S2_V, 1); // S2 Verde
    digitalWrite(S4_R, 0); digitalWrite(S4_V, 1); // S4 Verde
  }

  // 'h' -> HORIZONTAL AMARILLO
  if (f == 'h') {
    digitalWrite(S2_R, 0); digitalWrite(S2_A, 1); // S2 Amarillo
    digitalWrite(S4_R, 0); digitalWrite(S4_A, 1); // S4 Amarillo
  }
  
  // 'R' -> Todo Rojo
  if (f == 'R') { todoRojo(); }
}