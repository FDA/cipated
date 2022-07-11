from typing import List

import os
import pandas as pd

from cipa.waveforms import waveforms_to_df, Waveform


class EDCsvFile():
    """Encapsulated Data csv file

    This class encapsulates the logic to save waveforms to a comma separated
    value (CSV) file. This implementation uses Pandas to support storing the
    csv file compressed within a zip file.

    Attributes:
        edfilename (str): filename of the csv file
        ted_dataset_path (str): path to the directory containing the TED file
            and waveform files
        recordcount (int): number of waveforms
        header_size (int): number of rows reserved for the header
        recordsize (int): number of samples per waveform
        compression (str, optional): For on-the-fly compression of the csv
            file data. If 'infer' and '%s' path-like, then detect compression
            from the following extensions: '.gz', '.bz2', '.zip', '.xz', or
            '.zst' (otherwise no compression). Set to None for no compression.
            Defaults to 'infer'. See Pandas documentation for additional
            details.
    """
    def __init__(
            self,
            edfilename: str,
            ted_dataset_path: str = '.',
            recordcount: int = 0,
            header_size: int = 0,
            recordsize: int = 0,
            compression: str = 'infer'
                ):
        self.ted_dataset_path = ted_dataset_path
        self.edfilename = edfilename
        self.recordcount = recordcount
        self.header_size = header_size
        self.recordsize = recordsize
        self.compression = compression

    def save_waveforms(
            self, waveforms: List[Waveform]):
        """Save a list of waveforms to file.

        Args:
            waveforms (List[Waveform]): List of waveforms to save to file

        Returns:
            None.
        """
        wf_df = waveforms_to_df(waveforms)
        self.header_size = 1  # 1 Row for the header
        self.recordcount = wf_df.shape[1]
        self.recordsize = len(waveforms) + 1  # Number of waveforms plus time

        fn = os.path.join(self.ted_dataset_path, self.edfilename)
        wf_df.to_csv(fn, index=False, compression=self.compression)


class EDXlsxFile():
    """Encapsulated Data csv file

    This class encapsulates the logic to save waveforms to an xlsx file.
    This implementation uses Pandas to support storing the xlsx file using
    openpyxl.

    Attributes:
        edfilename (str): filename of the xlsx file
        ted_dataset_path (str): path to the directory containing the TED file
            and waveform files
        recordcount (int): number of waveforms
        header_size (int): number of rows reserved for the header
        recordsize (int): number of samples per waveform
    """
    def __init__(
            self,
            edfilename: str,
            ted_dataset_path: str = '.',
            recordcount: int = 0,
            header_size: int = 0,
            recordsize: int = 0
                ):
        self.ted_dataset_path = ted_dataset_path
        self.edfilename = edfilename
        self.recordcount = recordcount
        self.header_size = header_size
        self.recordsize = recordsize

    def save_waveforms(
            self, waveforms: List[Waveform],
            sheetname: str = 'Sheet1',
            xlsxwriter: pd.ExcelWriter = None):
        """Save a list of waveforms to a sheet in an xlsx file.

        Args:
            waveforms (List[Waveform]): List of waveforms to save
            sheetname (str): Name of the sheet where to store the waveforms
            xlsxwriter (pd.ExcelWriter, Optional): pd.ExcelWriter to be used
                to write to xslx. Defaults to None.

        Returns:
            None.
        """
        wf_df = waveforms_to_df(waveforms)
        self.header_size = 1  # 1 Row for the header
        self.recordcount = wf_df.shape[1]
        self.recordsize = len(waveforms) + 1  # Number of waveforms plus time

        if xlsxwriter is None:
            fn = os.path.join(self.ted_dataset_path, self.edfilename)
            if os.path.exists(fn):
                xlsxmode = 'a'
            else:
                xlsxmode = 'w'
            with pd.ExcelWriter(
                    fn, mode=xlsxmode, engine='openpyxl') as xlsxwriter:
                wf_df.to_excel(xlsxwriter, sheetname, index=False)
        else:
            wf_df.to_excel(xlsxwriter, sheetname, index=False)
