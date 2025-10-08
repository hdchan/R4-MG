from ..Models import ParsedDeckList


class ExportFormattable:
    @property
    def file_format(self) -> str:
        raise Exception
    
    @property
    def format_name(self) -> str:
        raise Exception
    
    def export(self,
               file_path: str,
               parsed_deck_list: ParsedDeckList) -> None:
        raise Exception
    
class Importable:
    @property
    def file_format(self) -> str:
        raise Exception
    
    @property
    def format_name(self) -> str:
        raise Exception
    
    def import_text(self, text: str) -> None:
        raise Exception

    

    

        
