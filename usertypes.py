#This file is used to define all of the User types (i.e. student, faculty, staff, etc.)


#TO-DO

#Write a getUserType() function

class User:
	
	#Initializer
	def __init__(self, first, middle, last, email, phone):
		self.first = first
		self.middle = middle
		self.last = last
		self.email = email
		self.phone = phone
		
	#Accessor functions
	def getFirst(self):
		return self.first
	
	def getMiddle(self):
		return self.middle
	
	def getMiddleInitial(self):
		if(len(self.getMiddle()) > 0):
			return self.middle[0]
		else:
			return ""
	
	def getLast(self):
		return self.last
	
	def getEmail(self):
		return self.email
	
	def getPhone(self):
		return self.phone
	
	def getUserType(self):
		return "User"
	
	#toString function
	def __str__(self):
		return self.getFirst() + " " + self.getMiddleInitial() + " " + self.getLast()

#This would be a Student	
class Student(User):
	def __init__(self, first, middle, last, email, phone):
		super().__init__(first, middle, last, email, phone)
		
	def __str__(self):
		return super().__str__() + ", student"
	
	def getUserType(self):
		return "Student"
		

#This would be a member of the faculty (i.e. a Professor)		
class Faculty(User):
	def __init__(self, first, middle, last, email, phone):
		super().__init__(first, middle, last, email, phone)
		
	def __str__():
		return super().__str__() + ", faculty member"
	
	def getUserType(self):
		return "Faculty"
	

#This would be a member of the school staff (i.e. a Registrar's office staff member)	
class StaffMember(User):
	def __init__(self, first, middle, last, email, phone):
		super().__init__(first, middle, last, email, phone)
		
	def __str__():
		return super().__str__() + ", staff member"
	
	def getUserType(self):
		return "Staff"
	
