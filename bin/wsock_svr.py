#!/usr/bin/python3
# -*- coding: utf-8 -*-
import asyncio
import websockets
import json
# motor controller
import Motor_Controller

# light:
import RPi.GPIO as pin_bcm12
pin_bcm12.setmode(pin_bcm12.BCM)
pin_bcm12.setup(12, pin_bcm12.OUT) 

# Todo: ここらでモーターコントローラー初期化
mc = Motor_Controller.Motor_Controller()

# Todo: Duty 比の値を保持する整数初期化（-100 to 100）
duty = 0

# Light Flag
flg_light = False

connected = set()

def process_msg(data):
	global flg_light
	global duty

	str_type = data["type"]
	if str_type == "change":
		duty = data["value"]
		# ここでモーターコントローラーに値セット
		# 単純に、値を PWM のデューティ比に設定すればいい。
		# mc.motor_run(int(duty))
		# ※今回、配線の結果、duty は 負値で前進となってしまった。
		mc.motor_run(int(duty) * -1)
            
	elif str_type == "light":
		light_flg = data["value"]
		# ==0:Off / !=0:On
		if(light_flg == 0):
			# GPIO 12(BCM)
			pin_bcm12.output(12, 0)
			flg_light = False
		else:
			pin_bcm12.output(12, 1) 
			flg_light = True

	elif str_type == "mode":
		print("str_type: mode : Do Nothing.")
	else:
		# do nothing
		print("unknown str_type:"+str_type)

@asyncio.coroutine
def controll_handler(websocket, path):
    global connected
    global duty
    global flg_light
    # Register
    connected.add(websocket)
    js_msg = {'type':'accepted',
    	'remote_address':websocket.remote_address}
    yield from websocket.send(json.dumps(js_msg))
    # 暫定:個別に初期値を送信。
    # 今後初期値のクライアントへの送信方法は変更すべき。
    js_msg = {'type':'change',
    	'value':duty}
    yield from websocket.send(json.dumps(js_msg))

    js_msg = {'type':'light',
    	'value':int(flg_light)}
    yield from websocket.send(json.dumps(js_msg))
    


    try:
        # Send current value: JSON.
        # msg = '{"type":"change","value":'+str(duty)+'}'
        while 1:
            msg = yield from websocket.recv()
            # JSON 形式の値を読み取り
            print(msg)
            data = json.loads(msg)
			# データに応じた処理
            process_msg(data)

            # クライアントに送信
            for ws in connected:
            	if (websocket.remote_address == ws.remote_address): 
            		#送信者のコマンドの場合は Type を上書きする。
            		str_type = 'acknowledged'
            	else:
            		str_type = data['type']
            	js_msg = {'type':str_type,
                	'value':str(data['value'])
                	}
            	yield from ws.send(json.dumps(js_msg))

    except:
        print('!!!!')	
        connected.remove(websocket)
    
start_server = websockets.serve(controll_handler, '0.0.0.0', 10502)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
