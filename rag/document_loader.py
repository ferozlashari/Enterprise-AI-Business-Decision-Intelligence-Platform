
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Enterprise Document Loader

Loads and prepares enterprise knowledge documents
for the RAG pipeline.

Supports:
- PDF
- CSV
- TXT
- Recursive knowledge-base scanning
- Row-level business documents
- Business aggregation documents
- Metadata preservation
- UTF-8 / Latin1 CSV support

Author : Feroz Ali
=========================================================
"""

from pathlib import Path
from typing import List

import pandas as pd

from llama_index.core import Document
from pypdf import PdfReader


class EnterpriseDocumentLoader:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        data_directory="knowledge_base",
        chunk_size=1000,
        create_business_summaries=True
    ):

        self.data_directory = Path(
            data_directory
        ).resolve()

        self.chunk_size = int(
            chunk_size
        )

        self.create_business_summaries = (
            bool(
                create_business_summaries
            )
        )

    # =====================================================
    # TEXT CHUNKING
    # =====================================================

    def chunk_text(
        self,
        text: str
    ) -> List[str]:

        if text is None:

            return []

        text = str(
            text
        ).strip()

        if not text:

            return []

        chunks = []

        # -------------------------------------------------
        # Character-based chunking
        # -------------------------------------------------

        for i in range(
            0,
            len(text),
            self.chunk_size
        ):

            chunk = text[
                i:i + self.chunk_size
            ].strip()

            if chunk:

                chunks.append(
                    chunk
                )

        return chunks

    # =====================================================
    # DOCUMENT CREATOR
    # =====================================================

    @staticmethod
    def create_document(
        text,
        metadata
    ):

        if not text:

            return None

        text = str(
            text
        ).strip()

        if not text:

            return None

        return Document(

            text=text,

            metadata=metadata

        )

    # =====================================================
    # PDF LOADER
    # =====================================================

    def load_pdf(
        self,
        file_path
    ) -> List[Document]:

        documents = []

        file_path = Path(
            file_path
        )

        try:

            reader = PdfReader(
                str(file_path)
            )

            for page_number, page in enumerate(
                reader.pages
            ):

                try:

                    text = page.extract_text()

                except Exception:

                    text = None

                if not text:

                    continue

                chunks = self.chunk_text(
                    text
                )

                for chunk_number, chunk in enumerate(
                    chunks
                ):

                    document = (
                        self.create_document(

                            chunk,

                            {

                                "source":
                                    str(file_path),

                                "file_name":
                                    file_path.name,

                                "type":
                                    "pdf",

                                "page":
                                    page_number + 1,

                                "chunk":
                                    chunk_number + 1

                            }

                        )
                    )

                    if document:

                        documents.append(
                            document
                        )

        except Exception as error:

            print(
                f"PDF Loading Failed: "
                f"{file_path} | {error}"
            )

        return documents

    # =====================================================
    # CSV ENCODING
    # =====================================================

    @staticmethod
    def read_csv(
        file_path
    ):

        encodings = [

            "utf-8",

            "utf-8-sig",

            "latin1",

            "cp1252"

        ]

        last_error = None

        for encoding in encodings:

            try:

                return pd.read_csv(

                    file_path,

                    encoding=encoding

                )

            except (
                UnicodeDecodeError,
                LookupError
            ) as error:

                last_error = error

            except Exception as error:

                last_error = error

        raise RuntimeError(
            f"Unable to read CSV: "
            f"{file_path} | {last_error}"
        )

    # =====================================================
    # CSV ROW TO TEXT
    # =====================================================

    @staticmethod
    def row_to_text(
        row
    ):

        text_parts = []

        for column, value in row.items():

            if pd.isna(value):

                continue

            text_parts.append(
                f"{column}: {value}"
            )

        return "\n".join(
            text_parts
        )

    # =====================================================
    # BUSINESS SUMMARY DOCUMENT
    # =====================================================

    @staticmethod
    def summary_document(
        title,
        content,
        file_path,
        summary_type
    ):

        text = (
            f"BUSINESS SUMMARY\n"
            f"================\n"
            f"{title}\n\n"
            f"{content}"
        )

        return Document(

            text=text,

            metadata={

                "source":
                    str(file_path),

                "file_name":
                    Path(file_path).name,

                "type":
                    "business_summary",

                "summary_type":
                    summary_type

            }

        )

    # =====================================================
    # SALES SUMMARY
    # =====================================================

    def create_sales_summary(
        self,
        df,
        file_path
    ):

        documents = []

        # -------------------------------------------------
        # Detect sales column
        # -------------------------------------------------

        sales_column = None

        for column in (
            "Sales",
            "sales",
            "Revenue",
            "revenue"
        ):

            if column in df.columns:

                sales_column = column

                break

        if sales_column is None:

            return documents

        # -------------------------------------------------
        # Convert sales to numeric
        # -------------------------------------------------

        sales = pd.to_numeric(

            df[sales_column],

            errors="coerce"

        )

        valid_sales = sales.dropna()

        if valid_sales.empty:

            return documents

        total_sales = float(
            valid_sales.sum()
        )

        average_sales = float(
            valid_sales.mean()
        )

        record_count = len(
            valid_sales
        )

        # -------------------------------------------------
        # Overall sales summary
        # -------------------------------------------------

        content = (

            f"Total sales: ${total_sales:,.2f}\n"
            f"Average sale per record: "
            f"${average_sales:,.2f}\n"
            f"Number of sales records: "
            f"{record_count}\n"
            f"Sales column: {sales_column}\n"

        )

        documents.append(

            self.summary_document(

                "Overall Sales Performance",

                content,

                file_path,

                "overall_sales"

            )

        )

        # -------------------------------------------------
        # Category analysis
        # -------------------------------------------------

        category_column = None

        for column in (
            "Category",
            "category"
        ):

            if column in df.columns:

                category_column = column

                break

        if category_column:

            temp = df.copy()

            temp["_sales"] = pd.to_numeric(

                temp[sales_column],

                errors="coerce"

            )

            category_summary = (

                temp
                .dropna(
                    subset=[
                        category_column,
                        "_sales"
                    ]
                )
                .groupby(
                    category_column
                )["_sales"]
                .agg(
                    [
                        "sum",
                        "mean",
                        "count"
                    ]
                )
                .sort_values(
                    "sum",
                    ascending=False
                )
            )

            lines = []

            for category, row in (
                category_summary.iterrows()
            ):

                lines.append(

                    f"Category: {category} | "
                    f"Total Sales: "
                    f"${float(row['sum']):,.2f} | "
                    f"Average Sale: "
                    f"${float(row['mean']):,.2f} | "
                    f"Orders: "
                    f"{int(row['count'])}"

                )

            if lines:

                documents.append(

                    self.summary_document(

                        "Sales Performance by Product Category",

                        "\n".join(lines),

                        file_path,

                        "category_sales"

                    )

                )

        # -------------------------------------------------
        # Region analysis
        # -------------------------------------------------

        region_column = None

        for column in (
            "Region",
            "region"
        ):

            if column in df.columns:

                region_column = column

                break

        if region_column:

            temp = df.copy()

            temp["_sales"] = pd.to_numeric(

                temp[sales_column],

                errors="coerce"

            )

            region_summary = (

                temp
                .dropna(
                    subset=[
                        region_column,
                        "_sales"
                    ]
                )
                .groupby(
                    region_column
                )["_sales"]
                .agg(
                    [
                        "sum",
                        "mean",
                        "count"
                    ]
                )
                .sort_values(
                    "sum",
                    ascending=False
                )
            )

            lines = []

            for region, row in (
                region_summary.iterrows()
            ):

                lines.append(

                    f"Region: {region} | "
                    f"Total Sales: "
                    f"${float(row['sum']):,.2f} | "
                    f"Average Sale: "
                    f"${float(row['mean']):,.2f} | "
                    f"Orders: "
                    f"{int(row['count'])}"

                )

            if lines:

                documents.append(

                    self.summary_document(

                        "Sales Performance by Region",

                        "\n".join(lines),

                        file_path,

                        "region_sales"

                    )

                )

        # -------------------------------------------------
        # Product analysis
        # -------------------------------------------------

        product_column = None

        for column in (
            "Product Name",
            "Product",
            "product_name",
            "product"
        ):

            if column in df.columns:

                product_column = column

                break

        if product_column:

            temp = df.copy()

            temp["_sales"] = pd.to_numeric(

                temp[sales_column],

                errors="coerce"

            )

            product_summary = (

                temp
                .dropna(
                    subset=[
                        product_column,
                        "_sales"
                    ]
                )
                .groupby(
                    product_column
                )["_sales"]
                .sum()
                .sort_values(
                    ascending=False
                )
                .head(50)
            )

            lines = []

            for product, value in (
                product_summary.items()
            ):

                lines.append(

                    f"Product: {product} | "
                    f"Total Sales: "
                    f"${float(value):,.2f}"

                )

            if lines:

                documents.append(

                    self.summary_document(

                        "Top Performing Products",

                        "\n".join(lines),

                        file_path,

                        "product_sales"

                    )

                )

        # -------------------------------------------------
        # Monthly sales analysis
        # -------------------------------------------------

        date_column = None

        for column in (
            "Order Date",
            "order_date",
            "Date",
            "date"
        ):

            if column in df.columns:

                date_column = column

                break

        if date_column:

            temp = df.copy()

            temp["_date"] = pd.to_datetime(

                temp[date_column],

                errors="coerce"

            )

            temp["_sales"] = pd.to_numeric(

                temp[sales_column],

                errors="coerce"

            )

            monthly = (

                temp
                .dropna(
                    subset=[
                        "_date",
                        "_sales"
                    ]
                )
                .groupby(
                    temp["_date"].dt.to_period("M")
                )["_sales"]
                .sum()
                .sort_index()
            )

            lines = []

            for period, value in (
                monthly.items()
            ):

                lines.append(

                    f"Month: {period} | "
                    f"Sales: "
                    f"${float(value):,.2f}"

                )

            if lines:

                documents.append(

                    self.summary_document(

                        "Monthly Sales Trend",

                        "\n".join(lines),

                        file_path,

                        "monthly_sales"

                    )

                )

        return documents

    # =====================================================
    # CSV LOADER
    # =====================================================

    def load_csv(
        self,
        file_path
    ) -> List[Document]:

        documents = []

        file_path = Path(
            file_path
        )

        try:

            df = self.read_csv(
                file_path
            )

            if df.empty:

                print(
                    f"CSV Empty: {file_path}"
                )

                return []

            # -------------------------------------------------
            # Normalize column names
            # -------------------------------------------------

            df.columns = [

                str(column).strip()

                for column in df.columns

            ]

            # -------------------------------------------------
            # Create row-level documents
            # -------------------------------------------------

            for index, row in df.iterrows():

                text = self.row_to_text(
                    row
                )

                if not text.strip():

                    continue

                document = (
                    self.create_document(

                        text,

                        {

                            "source":
                                str(file_path),

                            "file_name":
                                file_path.name,

                            "type":
                                "csv_row",

                            "row":
                                int(index)

                        }

                    )
                )

                if document:

                    documents.append(
                        document
                    )

            # -------------------------------------------------
            # Create business summaries
            # -------------------------------------------------

            if self.create_business_summaries:

                summary_documents = (
                    self.create_sales_summary(

                        df,

                        file_path

                    )
                )

                documents.extend(
                    summary_documents
                )

            print(
                f"CSV Loaded: "
                f"{file_path.name} | "
                f"Rows: {len(df)} | "
                f"Documents: {len(documents)}"
            )

        except Exception as error:

            print(

                f"CSV Loading Failed: "
                f"{file_path} | {error}"

            )

        return documents

    # =====================================================
    # TEXT LOADER
    # =====================================================

    def load_text(
        self,
        file_path
    ) -> List[Document]:

        documents = []

        file_path = Path(
            file_path
        )

        text = None

        # -------------------------------------------------
        # UTF-8
        # -------------------------------------------------

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

        except UnicodeDecodeError:

            pass

        # -------------------------------------------------
        # Latin1 fallback
        # -------------------------------------------------

        if text is None:

            try:

                with open(
                    file_path,
                    "r",
                    encoding="latin1"
                ) as file:

                    text = file.read()

            except Exception as error:

                print(

                    f"TXT Loading Failed: "
                    f"{file_path} | {error}"

                )

                return []

            except Exception as error:

                print(
                    f"TXT Loading Failed: "  
                    f"{file_path} | {error}"
                )    

            return []

        # -------------------------------------------------
        # Chunk
        # -------------------------------------------------

        chunks = self.chunk_text(
            text
        )

        for chunk_number, chunk in enumerate(
            chunks
        ):

            document = (
                self.create_document(

                    chunk,

                    {

                        "source":
                            str(file_path),

                        "file_name":
                            file_path.name,

                        "type":
                            "txt",

                        "chunk":
                            chunk_number + 1

                    }

                )
            )

            if document:

                documents.append(
                    document
                )

        return documents

    # =====================================================
    # LOAD ALL ENTERPRISE DOCUMENTS
    # =====================================================

    def load_all_documents(
        self
    ) -> List[Document]:

        all_documents = []

        # -------------------------------------------------
        # Knowledge base validation
        # -------------------------------------------------

        if not self.data_directory.exists():

            print(
                "=========================================="
            )

            print(
                "KNOWLEDGE BASE FOLDER MISSING"
            )

            print(
                self.data_directory
            )

            print(
                "=========================================="
            )

            return []

        # -------------------------------------------------
        # Scan recursively
        # -------------------------------------------------

        files = [

            file

            for file in self.data_directory.rglob("*")

            if file.is_file()

        ]

        print(
            f"Knowledge Base: "
            f"{self.data_directory}"
        )

        print(
            f"Files Found: {len(files)}"
        )

        # -------------------------------------------------
        # Process files
        # -------------------------------------------------

        for file in files:

            suffix = file.suffix.lower()

            try:

                if suffix == ".pdf":

                    documents = self.load_pdf(
                        file
                    )

                elif suffix == ".csv":

                    documents = self.load_csv(
                        file
                    )

                elif suffix in (
                    ".txt",
                    ".md"
                ):

                    documents = self.load_text(
                        file
                    )

                else:

                    continue

                all_documents.extend(
                    documents
                )

                print(

                    f"Processed: "
                    f"{file.name} | "
                    f"Documents: "
                    f"{len(documents)}"

                )

            except Exception as error:

                print(

                    f"Document Processing Failed: "
                    f"{file} | {error}"

                )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        print(
            "\n=========================================="
        )

        print(
            "ENTERPRISE DOCUMENT LOADING COMPLETE"
        )

        print(
            "=========================================="
        )

        print(
            f"Files: {len(files)}"
        )

        print(
            f"Total Documents: "
            f"{len(all_documents)}"
        )

        # -------------------------------------------------
        # Document type statistics
        # -------------------------------------------------

        statistics = {}

        for document in all_documents:

            document_type = (
                document.metadata.get(
                    "type",
                    "unknown"
                )
            )

            statistics[document_type] = (
                statistics.get(
                    document_type,
                    0
                ) + 1
            )

        print(
            "Document Types:"
        )

        for document_type, count in (
            statistics.items()
        ):

            print(
                f"  {document_type}: {count}"
            )

        return all_documents


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    loader = EnterpriseDocumentLoader()

    documents = (
        loader.load_all_documents()
    )

    print(
        "\nDocuments:",
        len(documents)
    )

    if documents:

        print(
            "\nFirst Document:\n"
        )

        print(
            documents[0].text[:1000]
        )

        print(
            "\nMetadata:\n"
        )

        print(
            documents[0].metadata
        )

        print(
            "\n=========================================="
        )

        print(
            "BUSINESS SUMMARY DOCUMENTS"
        )

        print(
            "=========================================="
        )

        summaries = [

            document

            for document in documents

            if document.metadata.get(
                "type"
            ) == "business_summary"

        ]

        print(
            "Summary documents:",
            len(summaries)
        )

        for document in summaries:

            print(
                "\n---",
                document.metadata.get(
                    "summary_type"
                ),
                "---"
            )

            print(
                document.text[:1500]
            )

