from app.models.db import db
from app.models.address import Address, AddressType
from typing import Optional, List, Dict
import logging
import uuid

logger = logging.getLogger(__name__)

class AddressService:
    
    @staticmethod
    def create_address(data: Dict) -> Dict:
        """
        Create a new address
        """
        try:
            # If this is set as default, unset other default addresses
            if data.get('is_default'):
                Address.query.filter_by(user_id=data['user_id']).update({'is_default': False})
            
            address = Address(
                id=str(uuid.uuid4()),
                user_id=data['user_id'],
                address_type=AddressType(data.get('address_type', 'home')),
                full_name=data['full_name'],
                phone=data['phone'],
                address_line1=data['address_line1'],
                address_line2=data.get('address_line2'),
                city=data['city'],
                state=data['state'],
                postal_code=data['postal_code'],
                country=data.get('country', 'India'),
                is_default=data.get('is_default', False)
            )
            
            db.session.add(address)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Address created successfully',
                'address': address
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create address error: {str(e)}")
            return {
                'success': False,
                'message': f'Create failed: {str(e)}'
            }
    
    @staticmethod
    def get_address_by_id(address_id: str) -> Optional[Address]:
        """
        Get address by ID
        """
        try:
            return Address.query.get(address_id)
        except Exception as e:
            logger.error(f"Get address error: {str(e)}")
        return None
    
    @staticmethod
    def get_user_addresses(user_id: str) -> List[Address]:
        """
        Get all addresses for a user
        """
        try:
            return Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc()).all()
        except Exception as e:
            logger.error(f"Get user addresses error: {str(e)}")
            return []
    
    @staticmethod
    def get_default_address(user_id: str) -> Optional[Address]:
        """
        Get user's default address
        """
        try:
            return Address.query.filter_by(user_id=user_id, is_default=True).first()
        except Exception as e:
            logger.error(f"Get default address error: {str(e)}")
        return None
    
    @staticmethod
    def update_address(address_id: str, data: Dict) -> Dict:
        """
        Update address
        """
        try:
            address = Address.query.get(address_id)
            if not address:
                return {
                    'success': False,
                    'message': 'Address not found'
                }
            
            # If setting as default, unset other default addresses
            if data.get('is_default'):
                Address.query.filter_by(user_id=address.user_id).update({'is_default': False})
            
            for key, value in data.items():
                if hasattr(address, key):
                    setattr(address, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Address updated successfully',
                'address': address
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update address error: {str(e)}")
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    @staticmethod
    def set_default_address(address_id: str) -> Dict:
        """
        Set address as default
        """
        return AddressService.update_address(address_id, {'is_default': True})
    
    @staticmethod
    def delete_address(address_id: str) -> Dict:
        """
        Delete address
        """
        try:
            address = Address.query.get(address_id)
            if address:
                db.session.delete(address)
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Address deleted successfully'
                }
            return {
                'success': False,
                'message': 'Address not found'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Delete address error: {str(e)}")
            return {
                'success': False,
                'message': f'Delete failed: {str(e)}'
            }
