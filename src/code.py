import asyncio
import time

class Batmobile:
    def __init__(self, max_speed: float, charged: bool, cleaned: bool = False):
        self.max_speed = max_speed
        self.charged   = charged
        self.cleaned   = cleaned

    # ----- async actions -----
    async def drive(self):
        print("Driving")
        await asyncio.sleep(2)      # simulate travel time (2 seconds)
        print("Finished driving")

    async def charge(self):
        if not self.charged:
            print("Car charging")
            await asyncio.sleep(3)  # simulate charge time (3 seconds)
            print("Car charged")
            self.charged = True
        else:
            print("Already at 100%")

    async def clean(self):
        print("Cleaning car")
        await asyncio.sleep(2)
        print("Car cleaned")
        self.cleaned = True

    # ----- blocking actions (run in threads) -----
    def start_engine(self):
        print("Starting engine")
        time.sleep(1)               # /!\ blocks (not asynchronous) /!\
        print("Engine started")

    def stop_engine(self):
        print("Stopping engine")
        time.sleep(1)              # /!\ blocks (not asynchronous) /!\
        print("Engine stopped")

class BatmobileContext:
    def __init__(self, batmobile: Batmobile):
        self.batmobile = batmobile

    async def __aenter__(self):
        # 1 Start engine in a thread (otherwise it will block the execution)
        self._engine = asyncio.create_task(
            asyncio.to_thread(self.batmobile.start_engine)
        )
        # 2 Charge and clean at the same time
        self._charge  = asyncio.create_task(self.batmobile.charge())
        self._clean   = asyncio.create_task(self.batmobile.clean())

        # 3 Wait for all three jobs
        await asyncio.gather(self._engine, self._charge, self._clean)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # Always shut down
        await asyncio.to_thread(self.batmobile.stop_engine)
        return False        # re‑raise errors

async def main():
    batmobile = Batmobile(600, charged=False)
    async with BatmobileContext(batmobile):
        await batmobile.drive()

if __name__ == "__main__":
    asyncio.run(main())