import pandas as pd
import numpy as np

def process_01082025():

    def calculate_discrete_values(df, prefix):
        """Calculate discrete values by subtracting consecutive columns"""
        columns = [col for col in df.columns if col.startswith(prefix)]
        discrete_df = pd.DataFrame()

        # Calculate discrete values (difference between consecutive heights)
        for i in range(len(columns) - 1):
            current_col = columns[i]
            next_col = columns[i + 1]
            new_col_name = f"discrete_{current_col}"
            discrete_df[new_col_name] = df[current_col] - df[next_col]
        # Add the last column as is (nothing to subtract from it)
        discrete_df[f"discrete_{columns[-1]}"] = df[columns[-1]]
        return discrete_df


    def find_max_column(df, prefix):
        """Find column name with maximum value for each row"""
        columns = [col for col in df.columns if col.startswith(prefix)]
        return pd.DataFrame(df[columns].idxmax(axis=1), columns=[f'{prefix}_max_column'])


    def calculate_ratio(df, prefix):
        """Calculate ratio of first half sum to second half sum"""
        def sum_first_half(row):
            non_negative_values = [value for value in row if value not in [-9999.0, 0.0, np.inf]]
            half_index = len(non_negative_values) // 2
            if len(non_negative_values) % 2 == 1:
                return sum(non_negative_values[:half_index]) + 0.5 * non_negative_values[half_index]
            else:
                return sum(non_negative_values[:half_index])
        def sum_last_half(row):
            non_negative_values = [value for value in row if value not in [-9999.0, 0.0, np.inf]]
            half_index = len(non_negative_values) // 2
            if len(non_negative_values) % 2 == 1:
                return sum(non_negative_values[half_index + 1:]) + 0.5 * non_negative_values[half_index]
            else:
                return sum(non_negative_values[half_index:])
        columns = [col for col in df.columns if col.startswith(prefix)]
        df_subset = df[columns]
        ratio = df_subset.apply(sum_first_half, axis=1) / df_subset.apply(sum_last_half, axis=1)
        return pd.DataFrame(ratio, columns=[f'{prefix}_ratio'])


    # Read the CSV data
    df = pd.read_csv(r"F:\GMU\GEDI\Luther\Result_20250107/Test.csv")
    discrete_cover = calculate_discrete_values(df, 'cover_')
    discrete_pai = calculate_discrete_values(df, 'pai_')
    max_discrete_cover = find_max_column(discrete_cover, 'discrete_cover')
    max_discrete_pai = find_max_column(discrete_pai, 'discrete_pai')
    max_pavd = find_max_column(df, 'pavd_')
    # 3. Calculate ratios
    cover_ratio = calculate_ratio(discrete_cover, 'discrete_cover')
    pai_ratio = calculate_ratio(discrete_pai, 'discrete_pai')
    pavd_ratio = calculate_ratio(df, 'pavd_')
    # Combine all results
    result = pd.concat([
        discrete_cover,
        discrete_pai,
        df[[col for col in df.columns if col.startswith('pavd_')]],
        max_discrete_cover,
        max_discrete_pai,
        max_pavd,
        cover_ratio,
        pai_ratio,
        pavd_ratio
    ], axis=1)
    output = r"F:\GMU\GEDI\Luther\Result_20250107/Ratio.csv"
    result.to_csv(output, index=None)


def process_01082025_2():
    df = pd.read_csv(r"F:\GMU\GEDI\Luther\Result_20250107/GEDI_list.csv")
    # Step 1: Calculate mean and std for each numerical column grouped by 'Site'
    numerical_columns = df.select_dtypes(include='number').columns
    stats = df.groupby('Site')[numerical_columns].agg(['mean', 'std'])

    # Step 2: Create frequency-based columns for categorical columns
    categorical_columns = ['discrete_cover_max_column', 'discrete_pai_max_column', 'pavd__max_column']

    # Step 1: Calculate frequency counts for each unique value in the categorical columns grouped by Site
    frequency_counts = {}
    for col in categorical_columns:
        counts = df.groupby('Site')[col].value_counts().unstack(fill_value=0)
        counts.columns = [f"{col}_{val}_count" for val in counts.columns]  # Rename columns to reflect value counts
        frequency_counts[col] = counts

    # Step 2: Combine all frequency counts into a single DataFrame
    frequency_counts_combined = pd.concat(frequency_counts.values(), axis=1)

    # Combine with the original stats DataFrame
    result = pd.concat([stats, frequency_counts_combined], axis=1)

    output = r"F:\GMU\GEDI\Luther\Result_20250107/Process_2.csv"
    result.to_csv(output, index=None)

process_01082025_2()