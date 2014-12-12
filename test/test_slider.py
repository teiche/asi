from time import sleep

from asi import client

if __name__ == '__main__':
    s = client.Slider()

    while True:
        s.to_acquisition()
        while not s.ready():
            pass

        sleep(2)

        s.to_science()
        while not s.ready():
            pass

        sleep(2)
