import pytest
import serpent.serpent as serp
import sys
from unittest.mock import patch, MagicMock


def testy_base() :
        with patch('builtins.print') as mock_print:
                with patch('builtins.input', return_value='YES') as mock_input:             
                        serp.setup_base()
                        mock_input.assert_called_once() 

     
                        

def test_ocr_choice() :
            with patch('builtins.input', return_value='ocr') as mock_input:
                    serp.setup_ocr()
                    mock_input.assert_called_once()
                    
                        

def test_gui_choice() :
            with patch('builtins.input', return_value='gui') as mock_input:
                    serp.setup_gui()
                    mock_input.assert_called_once()


def test_gui_choice() :
            with patch('builtins.input', return_value='ocr') as mock_input:
                    serp.setup_ocr()
                    mock_input.assert_called_once()

def test_ml_choice() :
            with patch('builtins.input', return_value='ml') as mock_input:
                    serp.setup_ml()
                    mock_input.assert_called()

                        

def test_random_choice() :
        with patch('builtins.print') as mock_print:          
                        serp.setup('123')
                        mock_print.assert_called_with("Invalid Setup Module: 123")



def test_execute_1() :
    with patch('builtins.print') as mock_print:
            sys.argv[1] = '--help'
            serp.execute()
            mock_print.assert_called()


def test_execute_ocr() :
    with patch('builtins.print') as mock_print:
        sys.argv[1] == 'ocr'
        serp.execute()
        mock_print.assert_called_with('')

def test_execute_setup() :
    with patch('builtins.print') as mock_print:
        sys.argv[1] == 'setup'
        serp.execute()
        mock_print.assert_called_with('')


def test_execute_ml() :
    with patch('builtins.print') as mock_print:
        sys.argv[1] == 'ml'
        serp.execute()
        mock_print.assert_called_with('')


def test_execute_gui() :
    with patch('builtins.print') as mock_print:
        sys.argv[1] == 'gui'
        serp.execute()
        mock_print.assert_called_with('')


def test_execute_modules() :
    with patch('builtins.print') as mock_print:
        sys.argv[1] == 'modules'
        serp.execute()
        mock_print.assert_called_with('')









   



                
          

