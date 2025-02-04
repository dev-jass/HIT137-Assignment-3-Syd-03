
def draw_sq():
    size = int(input("Enter the size of the square: "))
    if size < 1:
        print("Size must be 1 or greater.")
        return
    
    for i in range(size):
        if i == 0 or i == size - 1:  
            print('*' * size)
        else:  
            print('*' + ' ' * (size - 2) + '*')

# Execute function
print("Design square:")
draw_sq()

