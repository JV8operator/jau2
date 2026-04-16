def estimate_probability(cgpa, internships):

    if cgpa >= 8 and internships >= 2:
        return "High", "6-10 LPA"

    elif cgpa >= 7:
        return "Medium", "4-6 LPA"

    else:
        return "Low", "2-4 LPA"