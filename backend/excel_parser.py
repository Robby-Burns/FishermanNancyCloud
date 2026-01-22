import pandas as pd
from typing import List, Dict
import io


class ExcelParser:
    """Parse Excel files for buyer contact information"""

    def parse_buyers_excel(self, file_content: bytes) -> Dict[str, any]:
        """
        Parse Excel file with buyer contacts.
        
        Expected columns:
        - Buyer Name
        - Phone (10 digits, no formatting)
        - Carrier (verizon, att, tmobile, sprint)
        - Email (optional)
        - Preferred Fish (comma-separated)
        - Notes (optional)
        
        Returns:
            {
                "buyers": [
                    {
                        "name": "John Smith",
                        "phone": "3605551234",
                        "carrier": "verizon",
                        "email": "john@email.com",
                        "preferred_fish": "Halibut, Salmon",
                        "notes": "Text after 8am"
                    }
                ],
                "errors": ["Row 3: Invalid phone number", ...]
            }
        """
        try:
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_content))

            # Normalize column names (handle different capitalizations)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # Expected columns
            required_columns = ['buyer_name', 'phone', 'carrier']
            optional_columns = ['email', 'preferred_fish', 'notes']

            # Check for required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "buyers": [],
                    "errors": [f"Missing required columns: {', '.join(missing_columns)}"]
                }

            buyers = []
            errors = []

            # Process each row
            for index, row in df.iterrows():
                row_num = index + 2  # Excel row number (1-indexed + header)

                # Extract and validate data
                buyer = {}

                # Buyer Name
                name = str(row.get('buyer_name', '')).strip()
                if not name or name == 'nan':
                    errors.append(f"Row {row_num}: Missing buyer name")
                    continue
                buyer['name'] = name

                # Phone (clean and validate)
                phone = str(row.get('phone', '')).strip()
                phone = self._clean_phone(phone)
                if not phone or len(phone) != 10 or not phone.isdigit():
                    errors.append(f"Row {row_num}: Invalid phone number '{phone}'. Must be 10 digits.")
                    continue
                buyer['phone'] = phone

                # Carrier
                carrier = str(row.get('carrier', '')).strip().lower()
                valid_carriers = ['verizon', 'att', 'tmobile', 'sprint']
                if carrier not in valid_carriers:
                    errors.append(f"Row {row_num}: Invalid carrier '{carrier}'. Must be one of: {', '.join(valid_carriers)}")
                    continue
                buyer['carrier'] = carrier

                # Optional: Email
                email = str(row.get('email', '')).strip()
                buyer['email'] = email if email and email != 'nan' else None

                # Optional: Preferred Fish
                preferred_fish = str(row.get('preferred_fish', '')).strip()
                buyer['preferred_fish'] = preferred_fish if preferred_fish and preferred_fish != 'nan' else None

                # Optional: Notes
                notes = str(row.get('notes', '')).strip()
                buyer['notes'] = notes if notes and notes != 'nan' else None

                buyers.append(buyer)

            return {
                "buyers": buyers,
                "errors": errors
            }

        except Exception as e:
            return {
                "buyers": [],
                "errors": [f"Error parsing Excel file: {str(e)}"]
            }

    def _clean_phone(self, phone: str) -> str:
        """
        Clean phone number: remove formatting, keep only digits.
        
        Examples:
        - "(360) 555-1234" -> "3605551234"
        - "360-555-1234" -> "3605551234"
        - "3605551234" -> "3605551234"
        """
        # Remove all non-digit characters
        cleaned = ''.join(c for c in phone if c.isdigit())
        
        # Remove leading 1 if present (US country code)
        if len(cleaned) == 11 and cleaned.startswith('1'):
            cleaned = cleaned[1:]
        
        return cleaned

    def create_template_excel(self) -> bytes:
        """
        Create a template Excel file for buyers.
        
        Returns:
            Excel file content as bytes
        """
        # Sample data
        data = {
            'Buyer Name': ['John Smith', 'Mike Jones'],
            'Phone': ['3605551234', '3605555678'],
            'Carrier': ['verizon', 'att'],
            'Email': ['john@email.com', 'mike@email.com'],
            'Preferred Fish': ['Halibut, Salmon', 'Crab'],
            'Notes': ['Text after 8am', 'Prefers calls']
        }

        df = pd.DataFrame(data)

        # Write to Excel
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        return output.getvalue()
