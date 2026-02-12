def calculate_total_price(items_list):
    """
    Calculate the total price of active items.
    
    Args:
        items_list: List of item dictionaries with 'active' and 'price' keys
        
    Returns:
        float: Total price of all active items
    """
    total_price = 0.0
    
    for item in items_list:
        if item.get('active', False):
            total_price += item.get('price', 0.0)
    
    return total_price


def get_user_by_id(user_id):
    """
    Retrieve a user by their unique identifier.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        dict: User object if found, None otherwise
    """
    users = load_users()
    
    for user in users:
        if user.get('id') == user_id:
            return user
    
    return None
