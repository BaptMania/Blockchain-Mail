from multiprocessing import Process
import program_blockchain
import app


if __name__ == "__main__":
    procs = [Process(target=app.run), Process(target=program_blockchain.run)]

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
