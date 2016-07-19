from redis import StrictRedis


def sendQueue(channel, msg):
    redis = StrictRedis()
    redis.publish(channel, msg)
