def digital_root(n):
    """Calculates the digital root of a number until it's a single digit."""
    while n > 9:
        n = sum(int(digit) for digit in str(n))
    return n

def calculate_numerology(name, surname, birthdate):
    """
    Performs the 4 required numerology calculations.
    - name: string
    - surname: string
    - birthdate: string in format GG/MM/AAAA
    """
    full_name = (name + surname).upper()
    vowels = "AEIOU"
    
    # 1. Consonants
    # Takes consonants, converts to upper, sum (ASCII - 64), then digital root.
    cons_sum = 0
    for char in full_name:
        if char.isalpha() and char not in vowels:
            cons_sum += (ord(char) - 64)
    output_cons = digital_root(cons_sum)
    
    # 2. Vowels
    # Takes vowels, converts to upper, sum (ASCII - 64), then digital root.
    vocs_sum = 0
    for char in full_name:
        if char.isalpha() and char in vowels:
            vocs_sum += (ord(char) - 64)
    output_vocs = digital_root(vocs_sum)
    
    # 3. Sum of output_cons and output_vocs
    # Sum them, digital root.
    output_tots = digital_root(output_cons + output_vocs)
    
    # 4. Birth date
    # Sum all digits, digital root.
    date_digits_sum = sum(int(d) for d in birthdate if d.isdigit())
    output_data = digital_root(date_digits_sum)
    
    return {
        "output_cons": output_cons,
        "output_vocs": output_vocs,
        "output_tots": output_tots,
        "output_data": output_data
    }

# Example test
if __name__ == "__main__":
    result = calculate_numerology("MARIO", "ROSSI", "10/12/1990")
    print(f"Result: {result}")
