"""Synthetic resident profiles for local AquaNest dashboard demonstrations."""

RESIDENT_PROFILES = (
    {"userId": "USR_RES_1", "name": "Rajesh Sharma", "email": "rajesh@aquanest.io", "role": "RESIDENT", "houseId": "H101", "baseDailyUsageLitres": 230.0},
    {"userId": "USR_RES_2", "name": "Priya Venkatesh", "email": "priya@aquanest.io", "role": "RESIDENT", "houseId": "H102", "baseDailyUsageLitres": 260.0},
    {"userId": "USR_RES_3", "name": "Arun Kumar", "email": "arun@aquanest.io", "role": "RESIDENT", "houseId": "H103", "baseDailyUsageLitres": 290.0},
    {"userId": "USR_RES_4", "name": "Sneha Patel", "email": "sneha@aquanest.io", "role": "RESIDENT", "houseId": "H104", "baseDailyUsageLitres": 850.0},
    {"userId": "USR_RES_5", "name": "Vikram Malhotra", "email": "vikram@aquanest.io", "role": "RESIDENT", "houseId": "H105", "baseDailyUsageLitres": 320.0},
    {"userId": "USR_RES_6", "name": "Ananya Reddy", "email": "ananya@aquanest.io", "role": "RESIDENT", "houseId": "H106", "baseDailyUsageLitres": 350.0},
    {"userId": "USR_RES_7", "name": "Aditi Rao", "email": "resident107@aquanest.test", "role": "RESIDENT", "houseId": "H107", "baseDailyUsageLitres": 380.0},
    {"userId": "USR_RES_8", "name": "Kabir Mehta", "email": "resident108@aquanest.test", "role": "RESIDENT", "houseId": "H108", "baseDailyUsageLitres": 410.0},
    {"userId": "USR_RES_9", "name": "Meera Nair", "email": "resident109@aquanest.test", "role": "RESIDENT", "houseId": "H109", "baseDailyUsageLitres": 440.0},
    {"userId": "USR_RES_10", "name": "Rohan Das", "email": "resident110@aquanest.test", "role": "RESIDENT", "houseId": "H110", "baseDailyUsageLitres": 470.0},
    {"userId": "USR_RES_11", "name": "Isha Kapoor", "email": "resident111@aquanest.test", "role": "RESIDENT", "houseId": "H111", "baseDailyUsageLitres": 500.0},
    {"userId": "USR_RES_12", "name": "Neel Shah", "email": "resident112@aquanest.test", "role": "RESIDENT", "houseId": "H112", "baseDailyUsageLitres": 530.0},
    {"userId": "USR_RES_13", "name": "Kavya Iyer", "email": "resident113@aquanest.test", "role": "RESIDENT", "houseId": "H113", "baseDailyUsageLitres": 560.0},
    {"userId": "USR_RES_14", "name": "Dev Malhotra", "email": "resident114@aquanest.test", "role": "RESIDENT", "houseId": "H114", "baseDailyUsageLitres": 590.0},
    {"userId": "USR_RES_15", "name": "Tara Menon", "email": "resident115@aquanest.test", "role": "RESIDENT", "houseId": "H115", "baseDailyUsageLitres": 620.0},
    {"userId": "USR_RES_16", "name": "Aarav Gupta", "email": "resident116@aquanest.test", "role": "RESIDENT", "houseId": "H116", "baseDailyUsageLitres": 650.0},
    {"userId": "USR_RES_17", "name": "Diya Bose", "email": "resident117@aquanest.test", "role": "RESIDENT", "houseId": "H117", "baseDailyUsageLitres": 680.0},
    {"userId": "USR_RES_18", "name": "Samir Joshi", "email": "resident118@aquanest.test", "role": "RESIDENT", "houseId": "H118", "baseDailyUsageLitres": 710.0},
    {"userId": "USR_RES_19", "name": "Nisha Kulkarni", "email": "resident119@aquanest.test", "role": "RESIDENT", "houseId": "H119", "baseDailyUsageLitres": 740.0},
    {"userId": "USR_RES_20", "name": "Aditya Verma", "email": "resident120@aquanest.test", "role": "RESIDENT", "houseId": "H120", "baseDailyUsageLitres": 770.0},
)

RESIDENT_PROFILE_BY_HOUSE = {profile["houseId"]: profile for profile in RESIDENT_PROFILES}
RESIDENT_PROFILE_BY_EMAIL = {profile["email"].lower(): profile for profile in RESIDENT_PROFILES}
