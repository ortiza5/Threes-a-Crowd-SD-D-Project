import usertypes

# Use this as a test file. If we modify the usertypes we should run this
# file for testing. We should also add new test cases if we add more
# functionality to the usertypes.py file.


def Test1CreateUser():
    # The output of this file should be "Mark", "Justin", "J", \
    # "Uszacki", "uszacm@rpi.edu", "7324253901", "Mark J Uszacki, \
    # student"
    user1 = usertypes.Student("Mark", "Justin", "Uszacki",
                              "uszacm@rpi.edu", "7324253901")
    print(user1.getFirst())
    print(user1.getMiddle())
    print(user1.getMiddleInitial())
    print(user1.getLast())
    print(user1.getEmail())
    print(user1.getPhone())

    print(user1)


def Test2CreateDifferentUserTypes():
    # The output of this file should be "Student", "Faculty", \
    # "Staff", "User"
    user1 = usertypes.Student("Mark", "Justin", "Uszacki",
                              "uszacm@rpi.edu", "7324253901")
    user2 = usertypes.Faculty("Ann", "M", "Miller", "millea5@rpi.edu",
                              "5188158888")
    user3 = usertypes.StaffMember("David", "Xavier", "Davis",
                                  "davisd2@rpi.edu", "9088098989")
    user4 = usertypes.User("Andy", "William", "Cisive",
                           "cisiva@rpi.edu", "7188178181")
    # Get it? Andy Cisive? Indecisive? Yeah, that was a bad pun.
    print(user1.getUserType())
    print(user2.getUserType())
    print(user3.getUserType())
    print(user4.getUserType())

Test2CreateDifferentUserTypes()
