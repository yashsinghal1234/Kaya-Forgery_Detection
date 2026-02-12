def calculate_total(items):
    total=0
    for item in items:
        if item['active']:
            total+=item['price']
    return total

def get_user(id):
    # find user
    users=load_users()
    for u in users:
        if u['id']==id:
            return u
    return None
