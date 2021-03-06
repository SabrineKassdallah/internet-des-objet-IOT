# coding: utf8
""" université 

	Envoi des données température et senseur PIR vers serveur MQTT
 """ 

from machine import Pin, I2C, reset
import time
from ubinascii import hexlify
from network import WLAN

CLIENT_ID = '	spider'

# Utiliser résolution DNS (serveur en ligne) 
# MQTT_SERVER = 'test.mosquitto.org'
#
# Utiliser IP si le Pi en adresse fixe 
# (plus fiable sur réseau local/domestique)
# MQTT_SERVER = '192.168.8.220'
#
# Utiliser le hostname si Pi en DHCP et que la propagation du
# hostname atteind le modem/router (voir aussi gestion mDns sur router).
# (pas forcement fiable sur réseau domestique)
# MQTT_SERVER = 'pythonic'
#
# Attention: MicroPython sous ESP8266 ne gère pas mDns!

MQTT_SERVER = "192.168.8.210"

# Mettre a None si pas utile
MQTT_USER = 'IsitCom_HASHTAG_TOUNSI'
MQTT_PSWD = 'NuitDinfo'

# redemarrage auto après erreur 
ERROR_REBOOT_TIME = 3600 # 1 h = 3600 sec

# PIR
PIR_PIN = 13 # Signal du senseur PIR.
PIR_RETRIGGER_TIME = 15 * 60 # 15 min
# temps (sec) dernière activation PIR
last_pir_time = 0 
last_pir_msg  = "NONE"
# temps (sec) dernier envoi MSG
last_pir_msg_time = 0 
# Programme principal doit-il envoyer
# une notification "MOUV" rapidement?
fire_pir_alert = False 

# --- Demarrage conditionnel ---
runapp = Pin( 12,  Pin.IN, Pin.PULL_UP )
led = Pin( 0, Pin.OUT )
led.value( 1 ) # eteindre

def led_error( step ):
	global led
	t = time.time()
	while ( time.time()-t ) < ERROR_REBOOT_TIME:
		for i in range( 20 ):
			led.value(not(led.value()))
			time.sleep(0.100)
		led.value( 1 ) # eteindre
		time.sleep( 1 )
		# clignote nbr fois
		for i in range( step ):
			led.value( 0 ) 
			time.sleep( 0.5 )
			led.value( 1 )
			time.sleep( 0.5 )
		time.sleep( 1 )
	# Re-demarre l'ESP
	reset()

if runapp.value() != 1:
	from sys import exit
	exit(0)

led.value( 0 ) # allumer

# --- Programme Pincipal ---
from umqtt.simple import MQTTClient
try: 
	q = MQTTClient( client_id = CLIENT_ID, server = MQTT_SERVER, user = MQTT_USER, password = MQTT_PSWD )
	if q.connect() != 0:
		led_error( step=1 )
except Exception as e:
	print( e )
	# Verifier MQTT_SERVER, MQTT_USER, MQTT_PSWD
	led_error( step=2 ) 

# chargement des bibliotheques
try:
	from ads1x15 import *
	from machine import Pin
except Exception as e:
	print( e )
	led_error( step=3 )

# declare le bus i2c
i2c = I2C( sda=Pin(4), scl=Pin(5) )

# gestion du senseur PIR
def pir_activated( p ):
	# print( 'pir activated @ %s' % time.time() )
	global last_pir_time, last_pir_msg, fire_pir_alert 
	last_pir_time = time.time()
	# Faut-il lancer un message MOUV rapidement? 
	# Initialiser le drapeau pour la boucle principale
	fire_pir_alert = (last_pir_msg == "NONE")

# créer les senseurs
try:
	adc = ADS1115( i2c=i2c, address=0x48, gain=0 )

	pir_sensor = Pin( PIR_PIN, Pin.IN )
	pir_sensor.irq( trigger=Pin.IRQ_RISING, handler=pir_activated )
except Exception as e:
	print( e )
	led_error( step=4 )

try:
	# annonce connexion objet
	sMac = hexlify( WLAN().config( 'mac' ) ).decode()
	q.publish( "connect/%s" % CLIENT_ID , sMac )
except Exception as e:
	print( e )
	led_error( step=5 )

import uasyncio as asyncio

def capture_1h():
	""" Executé pour capturer des donnees chaque heure """
	global q
	global adc
	# tmp36 - senseur température and Humidity 
	valeur = adc.read( rate=0, channel1=0 )
	mvolts = valeur * 0.1875
	t = (mvolts - 500)/10
	t = "{0:.2f}".format(t)  # transformer en chaine de caractère ("Temp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
        h = "{0:.2f}".format(t) 
	q.publish( "université/rez/spider/temp", t )

def heartbeat():
	""" Led eteinte 200ms toutes les 10 sec """
	# PS: LED déjà éteinte par run_every!
	time.sleep( 0.2 )

def pir_alert():
	""" Envoyer un MOUV en urgence sur topic spider/pir 
	    si fire_pir_alert """
	global fire_pir_alert, last_pir_msg, last_pir_msg_time
	if fire_pir_alert:
		fire_pir_alert=False # desactiver l'alerte!
		last_pir_msg = "MOUV"
		last_pir_msg_time = time.time()
		q.publish( "université/rez/spider
/pir", last_pir_msg )

def Ultrason():
	""" Envoyer la distance  sur topic spider/Ultrason
	     """
	global fire_Ultrason_alert, last_Ultrason_msg, last_ultrason_msg_time
	if fire_Ultrason_alert:
		fire_Ultrason_alert=False # desactiver l'alerte!
		last_Ultrason_msg = "distance"
		last_Ultrason_msg_time = time.time()
		q.publish( "université/rez/spider

def pir_update():
	""" Mise à jour régulière du topic spider/pir """
	global last_pir_msg, last_pir_msg_time
	if (time.time() - last_pir_msg_time) < PIR_RETRIGGER_TIME:
		# ce n est pas le moment d envoyer un 
		# message de mise-a-jour
		return

	# PIR activé depuis les x dernière minutes
	if (time.time() - last_pir_time) < PIR_RETRIGGER_TIME:
		msg = "MOUV"
	else:
		msg = "NONE"
	
	# ne pas renvoyer les NONE
	if msg == "NONE" == last_pir_msg:
		return
	
	# Publier le msg
	last_pir_msg = msg
	last_pir_msg_time = time.time()
	q.publish( "université/rez/spider/pir", last_pir_msg )


async def run_every( fn, min= 1, sec=None):
	global led
	wait_sec = sec if sec else min*60
	while True:
		led.value( 1 ) # eteindre pendant envoi/traitement
		try:
			fn()
		except Exception:
			print( "run_every catch exception for %s" % fn)
			raise # quitter boucle 
		led.value( 0 ) # allumer
		await asyncio.sleep( wait_sec )

async def run_app_exit():
	""" fin d'execution lorsque quitte la fonction """
	global runapp
	while runapp.value()==1:
		await asyncio.sleep( 10 )
	return 

loop = asyncio.get_event_loop()
loop.create_task( run_every(capture_1h, min=60) )
loop.create_task( run_every(pir_alert, sec=10) )
loop.create_task( run_every(pir_update, min=5))
loop.create_task( run_every(heartbeat, sec=10) )
try:
	loop.run_until_complete( run_app_exit() )
except Exception as e :
	print( e )
	led_error( step=6 )

# Desactive l'IRQ
pir_sensor = Pin( PIR_PIN, Pin.IN )

loop.close()
led.value( 1 ) # eteindre 
print( "Fin!")
