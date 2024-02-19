import concurrent.futures
import datetime
import time

from config import wanted_actions

from utils.nodes import History, pick_best_waxnode
import random

class TrainManager:
    def __init__(self, worker=1, posrr=1896127, posm=1896127):
        self.worker = worker
        self.posrr = posrr
        self.posm = posm
        self.out = []
        self.sess = History(server="https://wax.greymass.com")

    def thread(self, n):
        try:
            if n == 0:
                for _ in range(4):
                    resp = self.sess.get_actions(account_name="rr.century", pos=self.posrr).json()["actions"]
                    for res in resp:
                        if res["action_trace"]["act"]["name"] in wanted_actions:
                            self.out.append(res)
                    self.posrr += len(resp)
                    if len(resp) == 0:
                        break
            else:
                for _ in range(2):
                    resp = self.sess.get_actions(account_name="m.century", pos=self.posm).json()["actions"]
                    for res in resp:
                        if res["action_trace"]["act"]["name"] in ["usefuel", "buyfuel"]:
                            self.out.append(res)
                    self.posm += len(resp)
                    if len(resp) == 0:
                        break 

        except Exception as e:
            server = random.choice(pick_best_waxnode("history", 9))
            self.sess.server = server
            time.sleep(2)
    def fetch(self):
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2*self.worker) as executor:
            executor.submit(self.thread, 0)
            executor.submit(self.thread, 1)

        if time.time() - start < 2:
            time.sleep(2 - (time.time() - start))

    def test(self):
        search = True
        while search:
            try:
                res = self.sess.get_actions(account_name="m.century", pos=self.posm).json()
                jst = res["actions"]
                stm = jst[-1]["action_trace"]["block_time"]
                print(stm, self.posm)
            except Exception as e:
                print(e, res)
                search = False
                time.sleep(10)

                fin = self.posm - 75000
            self.posm += 75000
            time.sleep(0.5)

        print(fin)
        print(int(self.pos + (1000 * ((datetime.utcnow() - datetime.fromisoformat(stm)).total_seconds() / 60)) - 10000))

        return fin
