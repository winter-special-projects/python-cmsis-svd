# Python CMSIS SVD

Parser to read CMSIS SVD files, export Python code suitable for loading into MicroPython / CircuitPython `uctypes` structures. Very much early work in progress.

## Usage

SVD file from one of the CMSIS packs from your MCU maker, e.g. `ATSAMD51G19A.svd`:

```
python3 transform.py ATSAMD51G19A.svd
```

=>

directory `ATSAMD51G19A` with one Python file for each peripheral e.g. `PORT.py`:

```python
PORT = {
    DIR: 0x0 | uctypes.UINT32,
    DIRCLR: 0x4 | uctypes.UINT32,
    DIRSET: 0x8 | uctypes.UINT32,
    DIRTGL: 0xC | uctypes.UINT32,
    OUT: 0x10 | uctypes.UINT32,
    OUTCLR: 0x14 | uctypes.UINT32,
    OUTSET: 0x18 | uctypes.UINT32,
    OUTTGL: 0x1C | uctypes.UINT32,
    IN: 0x20 | uctypes.UINT32,
    CTRL: 0x24 | uctypes.UINT32,
    WRCONFIG: 0x28 | uctypes.UINT32,
    EVCTRL: 0x2C | uctypes.UINT32,
    PMUX: (0x30 | uctypes.ARRAY, 16 | uctypes.UINT8),
    PINCFG: (0x40 | uctypes.ARRAY, 32 | uctypes.UINT8),
}
```

You can optionally `mpy-cross` compile these:

```
for f in *.py; do ~/mpy-cross/mpy-cross $f; done
```

Leaving e.g.

```
silver-surfer ATSAMD51G19A :) $ ls
AC.mpy			ITM.mpy			SERCOM2.mpy
ADC0.mpy		MCLK.mpy		SERCOM3.mpy
ADC1.mpy		MPU.mpy			SERCOM4.mpy
AES.mpy			NVIC.mpy		SERCOM5.mpy
CCL.mpy			NVMCTRL.mpy		SUPC.mpy
CMCC.mpy		OSC32KCTRL.mpy		SysTick.mpy
CoreDebug.mpy		OSCCTRL.mpy		SystemControl.mpy
DAC.mpy			PAC.mpy			TC0.mpy
DMAC.mpy		PCC.mpy			TC1.mpy
DSU.mpy			PDEC.mpy		TC2.mpy
DWT.mpy			PM.mpy			TC3.mpy
EIC.mpy			PORT.mpy		TCC0.mpy
ETM.mpy			QSPI.mpy		TCC1.mpy
EVSYS.mpy		RAMECC.mpy		TCC2.mpy
FPU.mpy			RSTC.mpy		TPIU.mpy
FREQM.mpy		RTC.mpy			TRNG.mpy
GCLK.mpy		SDHC0.mpy		USB.mpy
HMATRIX.mpy		SERCOM0.mpy		WDT.mpy
ICM.mpy			SERCOM1.mpy
```

which can be cherry-picked across to your `lib` folder.

## Example Usage

Reproduce my basic clock manipulation example, sending a 1kHz square wave to D13 without any active CPU involvement, just writing registers. This is running on an Adafruit ItsyBitsy M4 Express, so has G19A version of the SAMD51 chip. First, copy useful shims across:

```
silver-surfer ATSAMD51G19A :) $ cp PORT.mpy GCLK.mpy MCLK.mpy TCC1.mpy /Volumes/CIRCUITPY/lib
silver-surfer ATSAMD51G19A :) $ ls -l PORT.mpy GCLK.mpy MCLK.mpy TCC1.mpy 
-rw-r--r--  1 graeme  staff  141 30 May 05:11 GCLK.mpy
-rw-r--r--  1 graeme  staff  223 30 May 05:11 MCLK.mpy
-rw-r--r--  1 graeme  staff  286 30 May 05:11 PORT.mpy
-rw-r--r--  1 graeme  staff  897 30 May 05:11 TCC1.mpy
```

Obviously you can also just copy / paste the structure definitions into your own source code. The usage is to first create the `struct`s with the correct base address (from the data sheet) then poke and prod the registers. Yes, I could add the `port` address and so on to the library...

```python
import uctypes

from PORT import PORT
from GCLK import GCLK
from MCLK import MCLK
from TCC1 import TCC1

port = uctypes.struct(0x41008000, PORT, uctypes.LITTLE_ENDIAN)
gclk = uctypes.struct(0x40001C00, GCLK, uctypes.LITTLE_ENDIAN)
mclk = uctypes.struct(0x40000800, MCLK, uctypes.LITTLE_ENDIAN)
tcc1 = uctypes.struct(0x41018000, TCC1, uctypes.LITTLE_ENDIAN)

port.PINCFG[22] |= 1
port.PMUX[11] |= 5

gclk.GENCTRL[4] = (0x1 << 16) | (0x1 << 8) | 0x7
gclk.PCHCTRL[25] = (0x1 << 6) | 0x4

mclk.APBBMASK |= 0x1 << 12

tcc1.WAVE = 2
tcc1.PER = 119999
tcc1.CC[2] = 60000
tcc1.CTRLA = 2
```

Writes out a square wave to D13 at 1kHz as the system clock is 120MHz.
