# Automated Dataset Analysis

## Dataset Summary
- Number of Rows: 10000
- Number of Columns: 23
### Columns and Data Types:
- book_id: int64
- goodreads_book_id: int64
- best_book_id: int64
- work_id: int64
- books_count: int64
- isbn: object
- isbn13: float64
- authors: object
- original_publication_year: float64
- original_title: object
- title: object
- language_code: object
- average_rating: float64
- ratings_count: int64
- work_ratings_count: int64
- work_text_reviews_count: int64
- ratings_1: int64
- ratings_2: int64
- ratings_3: int64
- ratings_4: int64
- ratings_5: int64
- image_url: object
- small_image_url: object

## Analysis Narrative
Based on the provided dataset summary, we can derive several insights and analyses about the book dataset. Here’s a breakdown of key points:

### General Overview
- **Size**: The dataset contains 10,000 rows and 23 columns, which is a reasonable size for analysis and allows for various types of insights.
- **Data Types**: The columns consist of integers, floating-point numbers, and objects (strings). This diversity allows for both quantitative analysis (e.g., ratings, counts) and qualitative analysis (e.g., titles, authors).

### Missing Values
- **ISBN**: There are 700 missing values in the `isbn` column, which could affect the ability to uniquely identify books.
- **ISBN13**: This column has 585 missing values, which is also significant as it could hinder linking to external databases.
- **Original Publication Year**: 21 missing values here might limit the ability to perform temporal analyses related to publication trends.
- **Original Title**: A substantial number of missing values (590) could affect the analysis of book titles.
- **Language Code**: 1,084 missing values in this column indicate a significant gap, suggesting that language distribution analysis will be incomplete.

### Sample Data Insights
- The dataset includes popular titles such as:
  - "The Hunger Games" by Suzanne Collins
  - "Harry Potter and the Sorcerer's Stone" by J.K. Rowling
  - "Twilight" by Stephenie Meyer
  - "To Kill a Mockingbird" by Harper Lee
  - "The Great Gatsby" by F. Scott Fitzgerald

- **Ratings**:
  - The average ratings range from 3.57 (Twilight) to 4.44 (Harry Potter), indicating a generally high level of satisfaction among readers.
  - The ratings counts are substantial, with "The Hunger Games" receiving over 4.7 million ratings, which could indicate its popularity and influence.

### Distribution Insights
- **Authors**: The dataset features multiple authors, suggesting potential studies on author popularity and collaboration.
- **Language Code**: The presence of diverse language codes (though with many missing values) allows for analysis of language preferences among readers.

### Rating Distribution
- The columns for ratings (from 1 to 5) indicate the distribution of reader evaluations:
  - For instance, "The Hunger Games" has the highest count of 5-star ratings (over 2.7 million
## Visualizations
1. Correlation Matrix:
![Correlation Matrix](correlation_matrix.png)
2. Distribution Plot:
![Distribution Plot](distribution_plot.png)
