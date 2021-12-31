from pyModbusTCP.server import ModbusServer, DataBank
import asyncio
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

async def main(test=False, stop_event=None, started=None):
    server = ModbusServer(host='127.0.1.101', port=1024, no_block=True)
    server.start()
    if not test:
        clear()
    else:
        started.set()
    await asyncio.create_task(loop(test, stop_event))
    server.stop()

async def loop(test=False, stop_event=None):
    while True:
        await asyncio.sleep(1)
        status = DataBank.get_bits(16, 1)[0]
        order = DataBank.get_words(255, 1)[0]
        amount = DataBank.get_words(0, 1)[0]
        
        if amount > 0 and status:
            amount -= 1
            DataBank.set_words(0, [amount])

        if amount == 0 and status:
            status = False
            DataBank.set_bits(16, [0])

        if not test:
            clear()
            print('Running' if status else 'Stopped')
            print(f'Current order: {order}')
            print(f'Remains to be done: {amount}')
            print('Ctrl+C to stop the server')
        else:
            if stop_event.is_set():
                break

def test_server(test, stop_event, started):
    asyncio.run(main(test=True, stop_event=stop_event, started=started))

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear()