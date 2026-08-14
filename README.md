# bikeshare

Núcleo de cobro y alquiler de un servicio de bicicletas compartidas de ciudad: tarifas, autorización de riders, ciclo de vida del alquiler y ocupación de estaciones.

Este repositorio es el código sobre el que se trabaja la **Hoja de Trabajo 2** del curso *Calidad y Automatización en Ingeniería de Software* (UFM, Semestre 2 2026). El enunciado completo está en [`HDT-2.pdf`](HDT-2.pdf) y la entrega es por MiU.

## Cómo correrlo

Requiere [uv](https://docs.astral.sh/uv/). No hay dependencias de producción.

```bash
git clone https://github.com/danihrndzld/hdt2-bikeshare.git
cd hdt2-bikeshare
uv sync

uv run bikeshare demo
uv run bikeshare quote --minutes 95 --electric --peak
```

La suite que viene incluida cubre el camino feliz de cada módulo, nada más:

```bash
uv run pytest
uv run pytest --cov --cov-report=html:cobertura --cov-report=term
```

La configuración de cobertura ya está en `pyproject.toml`: mide el paquete `bikeshare`, incluye cobertura de ramas y deja fuera la interfaz de línea de comandos, que es solo una cáscara de demostración.

## Reglas del negocio

Esta sección es la especificación del servicio. Es la referencia contra la que se comparan los resultados.

### Tarifas

- El tiempo se cobra en minutos completos.
- Los primeros **15 minutos** de cada alquiler no tienen costo.
- De **16 a 60 minutos** se cobra **Q15.00**.
- De **61 a 180 minutos** se cobra **Q15.00** más **Q10.00** por cada hora empezada después de la primera. Un alquiler de 61 minutos paga Q25.00; uno de 121 minutos paga Q35.00.
- Arriba de **180 minutos** se cobra la tarifa de día, **Q90.00**.
- Un alquiler no puede pasar de **1440 minutos**. Cotizar una duración mayor se rechaza.
- Una duración negativa se rechaza. Una duración que no sea un número entero de minutos también.

### Recargos

- Bicicleta eléctrica: **20%** sobre la tarifa base.
- Alquiler sin membresía: **Q5.00** de desbloqueo.
- Hora pico: **Q5.00**. Los miembros no pagan este recargo.
- El total de un alquiler nunca pasa de **Q100.00**.

### Autorización

Antes de soltar una bicicleta se revisan tres cosas, en este orden:

1. La cuenta está activa, es decir ni suspendida ni cerrada.
2. La cuenta no tiene saldo pendiente.
3. La estación tiene al menos una bicicleta disponible.

Si alguna falla se rechaza el alquiler y se reporta **la primera** que falló, con el código `account_inactive`, `balance_due` o `no_bikes_available`.

### Ciclo de vida del alquiler

- Al reservar, la bicicleta sale de la estación y el alquiler queda en `reserved`.
- La reserva se sostiene **10 minutos**. Si el alquiler se inicia después de ese plazo, la reserva pasa a `cancelled` y el intento falla.
- Un alquiler en `reserved` se puede cancelar; ahí termina.
- Solo un alquiler en `active` se puede cerrar. Al cerrarlo la bicicleta se ancla en la estación de destino, el alquiler pasa a `completed` y se emite el cobro.
- Si la estación de destino no tiene espacio, el cierre falla y el alquiler sigue en `active`.
- Un alquiler que estuvo abierto más de 1440 minutos pasa a `lost` y no se cobra.
- Cualquier otro evento que reciba un estado que no lo espera se rechaza.

### Estaciones

- Una estación tiene capacidad fija y no puede recibir más bicicletas que su capacidad.
- Tomar una bicicleta de una estación vacía falla. Pedir una bicicleta que no está anclada ahí también falla.
- Anclar una bicicleta que ya está anclada en esa estación falla.
- Una estación necesita rebalanceo cuando su ocupación es de **20% o menos**, o de **80% o más**. Una estación de capacidad 0 nunca lo necesita.

### El reloj

El paquete no lee el reloj del sistema. Quien llama pasa `now` como un entero de minutos en el reloj del servicio, y así los resultados son reproducibles.

## Estructura

```
src/bikeshare/
  accounts.py     cuentas de riders y su estado
  eligibility.py  autorización para iniciar un alquiler
  errors.py       jerarquía de excepciones del dominio
  fares.py        tarifas, recargos y tope
  rentals.py      el alquiler y sus transiciones
  stations.py     estaciones, anclajes y rebalanceo
  cli.py          interfaz de línea de comandos
tests/
  test_smoke.py   la suite incluida
```

## Licencia

MIT.
