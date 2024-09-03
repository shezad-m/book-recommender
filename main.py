"""
Book Recommender

This script allows the user to input the ISBN of a book and will
recommend a similar one based on past ratings of a wide collection of
books.

This tool requires three comma separated value files (.csv) named
Books.csv, Ratings.csv, and Users.csv contained in the dataset folder.

This script requires that `pandas` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * get_name_from_isbn - looks up the name of a book from its ISBN
    * find_most_similar - returns the most similar book
    * prep_dataset - returns a triple of the datasets
    * main - the main function of the script
"""

import pandas as pd


def get_name_from_isbn(books: pd.DataFrame, isbn: str) -> str:
    """
    Returns the name of a book from its ISBN

    Parameters
    ----------
    books : pd.DataFrame
        The dataset of books
    isbn : str
        The ISBN of the book to be queried

    Returns
    -------
    str
        The name of the book
    """
    return books[books['ISBN'] == isbn].iloc[0]['Book-Title']


def find_most_similar(ratings: pd.DataFrame, book_id: str) -> str:
    """
    Returns the ISBN of the most similar book to the input book

    Parameters
    ----------
    ratings : pd.DataFrame
        The dataset of ratings
    book_id : str
        The ISBN of the book

    Returns
    -------
    str
        The ISBN of the recommended book
    """

    # Get list of books liked by users who liked the input book
    book_ratings = ratings[(ratings['ISBN'] == book_id)
                           & (ratings['Book-Rating'] > 8)]
    sim_users = book_ratings['User-ID'].unique()
    sim_user_recs = ratings[(ratings['User-ID'].isin(sim_users))
                            & (ratings['Book-Rating'] > 8)]['ISBN']

    # Get the sublist of books liked by at least 5% of those who liked
    # the input book.
    sim_user_recs = sim_user_recs.value_counts() / len(sim_users)
    sim_user_recs = sim_user_recs[sim_user_recs > 0.05]

    # Out of users with similar tastes, compute the proportion of those
    # who 
    all_users = ratings[(ratings['ISBN'].isin(sim_user_recs.index))
                        & (ratings['Book-Rating'] > 8)]
    all_users_recs = (all_users['ISBN'].value_counts()
                      / len(all_users['User-ID'].unique()))
    rec_percentages = pd.concat([sim_user_recs, all_users_recs],
                                axis=1)
    rec_percentages.columns = ['Similar', 'All']
    rec_percentages['Score'] = (rec_percentages['Similar']
                                / rec_percentages['All'])
    rec_percentages = rec_percentages.sort_values('Score',
                                                  ascending=False)

    return rec_percentages[rec_percentages.index
                           != book_id].iloc[0].name


def prep_dataset() -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    Returns a 3-tuple of pd.DataFrames consisting of books, ratings,
    and users

    Returns
    -------
    (pd.DataFrame, pd.DataFrame, pd.DataFrame)
        A triple of DataFrames of books, ratings, users
    """
    books = pd.read_csv('dataset/Books.csv')
    ratings = pd.read_csv('dataset/Ratings.csv')
    users = pd.read_csv('dataset/Users.csv')

    # Removes unnecessary columns from the DataFrames and any rows
    # that contain null values
    books.drop(columns=['Image-URL-S', 'Image-URL-M', 'Image-URL-L'],
               inplace=True)
    books_na = books.index[(books['Book-Author'].isna())
                           | (books['Publisher'].isna())]
    books.drop(index=books_na, inplace=True)

    users.drop(columns=['Age'], inplace=True)

    ratings_na = ratings.index[~ratings['ISBN'].isin(books['ISBN'])]
    ratings.drop(index=ratings_na, inplace=True)

    return books, ratings, users


def main():
    books, ratings, users = prep_dataset()

    while True:
        input_book = input("Enter a book's ISBN:")
        try:
            input_book_name = get_name_from_isbn(books, input_book)
            output_isbn = find_most_similar(ratings, input_book)
            output_name = get_name_from_isbn(books, output_isbn)
            out_str = 'If you like "{0}",then you\'ll like "{1}".'
            out_str = out_str.format(input_book_name, output_name)
        except IndexError:
            out_str = 'That book does not exist in the dataset.'
        print(out_str)


if __name__ == "__main__":
    main()
