import pandas as pd
import numpy as np

s = 10
df = pd.DataFrame({"Country": np.random.choice(["USA America", "JPY", "MEX", "IND", "AUS"], s),   
			 "employee": np.random.choice(["Bob", "Sam", "John", "Tom", "Harry"], s),
			 "economy_cat": np.random.choice(["developing","develop"], s),
		  "Net": np.random.randint(5, 75, s),
	})



print(len(df[(df['Country'] == 'JPY') & (df['economy_cat'] == 'develop') & (df['employee'] == 'John')]))