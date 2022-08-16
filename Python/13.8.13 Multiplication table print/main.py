# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# list of multiplication items: create list in list
L = [[(i + 1) * (j + 1) for j in range(10)] for i in range(10)]

# print header
print("{0:^3} | {1:^3} {2:^3} {3:^3} {4:^3} {5:^3} {6:^3} {7:^3} {8:^3} {9:^3}".format("*",
    L[0][1], L[0][2], L[0][3], L[0][4], L[0][5], L[0][6], L[0][7], L[0][8], L[0][9]))
print("".join([("+" if i == 4 else "-") for i in range(41)]))

# print other lines
for r in L[1:]:
    print("{0:^3} | {1:^3} {2:^3} {3:^3} {4:^3} {5:^3} {6:^3} {7:^3} {8:^3} {9:^3}".format(r[0],
        r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
