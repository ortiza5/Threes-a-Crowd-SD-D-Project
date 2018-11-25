import jsonpickle
import usertypes

user = usertypes.Student('a', 'b', 'c', 'd@d.d', '123')
pickled = jsonpickle.encode(user)
print(pickled)
unpickled = jsonpickle.decode(pickled)
print(unpickled.getUserType())
print(unpickled)
