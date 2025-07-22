# -*-coding:utf-8 -*-
package1 = {
    "param1": 10,
    "param2": "value2",
    "param3": True
}

package2 = {
    "param1": 15,
    "param2": "value2",
    "param3": False
}

def compare_packages(package1, package2):
    differences = {}
    for key in package1:
        if key in package2 and package1[key]!= package2[key]:
            differences[key] = (package1[key], package2[key])
    for key in package2:
        if key not in package1:
            differences[key] = (None, package2[key])

    return differences

result = compare_packages(package1, package2)
print(result)