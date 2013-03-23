package netlogoLink;

import java.util.LinkedHashMap;
import java.text.ParseException;
import org.nlogo.api.LogoList;

public class NLResult {
	private String type = null;
	private Object resultValue = null;
	private Integer NumberNestedLists = null;
	private String[] NestedTypes = null;
	
	public void setResultValue(Object o) throws Exception {
		logoToType(o);
	}
	
	public String getType() {
		return type;
	}

	public String getResultAsString() {
		return ((String)resultValue).toString();
	}
	
	public double getResultAsDouble() {
		return ((Double)resultValue).doubleValue();
	}
	
	public boolean getResultAsBoolean() {
		return ((Boolean)resultValue).booleanValue();
	}
	
	public Integer getResultAsInteger() {
		return (Integer)resultValue;
	}
	
	public double[] getResultAsDoubleArray() {
		return (double[])resultValue;
	}

	public int[] getResultAsIntegerArray() {
		return (int[])resultValue;
	}	
	
	public boolean[] getResultAsBooleanArray() {
		return (boolean[])resultValue;
	}

	public String[] getResultAsStringArray() {
		return (String[])resultValue;
	}	
	
	public Object getResultAsObject() {
		return resultValue;
	}
	
	public Object[] getResultAsObjectArray() {
		return (Object[])resultValue;
	}
		
	private void logoToType( Object o ) throws Exception {
		if(o instanceof LogoList)
		{
			type = "LogoList";
			org.nlogo.api.LogoList loli = (org.nlogo.api.LogoList)o;
			resultValue = cast_logolist(loli, false);
		}
		else if (o instanceof String) {
			type = "String";
			resultValue = ((String)o).toString();
		}
		else if (o instanceof Integer) {
			type = "Integer";
			resultValue = ((Integer)o).intValue();
		}
		else if (o instanceof Double) {
			type = "Double";
			resultValue = ((Double)o).doubleValue();
		}
		else if (o instanceof Boolean) {
			type = "Boolean";
			resultValue = ((Boolean)o).booleanValue();
		}
		else {
			type = "Unknown";
			resultValue = null;
			throw new Exception("Found unknown datatype: "+o);
		}
	}
	
	

	private Object cast_logolist(LogoList logolist, Boolean recursive) throws Exception
	{
	/**
	 * Method to transform a NetLogo List and put via rni.
	 * @param obj instance of LogoList
	 * @return long containing rni reference value
	 */	
		try
		{
			
    		if (logolist.get(0) instanceof LogoList)
    		{ 
    			Object[] lilist = new Object[logolist.size()];
    			NestedTypes = new String[logolist.size()];
				for (int i=0; i<logolist.size(); i++)
				{
					NLResult nestedResult = new NLResult();
					nestedResult.setResultValue(logolist.get(i));
					lilist[i] = nestedResult;
				}
    			type = "NestedList";
				return lilist;
    		}

    	    if (logolist.get(0) instanceof java.lang.String)
    	    {
           		String[] stringlist = new String[logolist.size()];
				for (int i=0; i<logolist.size(); i++)
				{
					stringlist[i] = (String)logolist.get(i);
				}
				if (!recursive)
					type = "StringList";
				return stringlist;
    	    }		    	    

    	    if (logolist.get(0) instanceof java.lang.Double)
    	    {
				double[] dblist = new double[logolist.size()];
				for (int i=0; i<logolist.size(); i++)
				{
					dblist[i] = ((java.lang.Double)logolist.get(i)).doubleValue();
				}     	
				if (!recursive)
					type = "DoubleList";
				return dblist; 	
    	   }   		    	   

    	   if (logolist.get(0) instanceof java.lang.Boolean)
    	   {
    	       	boolean[] boollist = new boolean[logolist.size()];
				for (int i=0; i<logolist.size(); i++)
				{
					if (!recursive)
						type = "BoolList";
					boollist[i] = ((java.lang.Boolean)logolist.get(i)).booleanValue();
				}
				return boollist;
    	   }
    	   
    	   if (logolist.get(0) instanceof java.lang.Integer)
    	   {
    	       	int[] intlist = new int[logolist.size()];
				for (int i=0; i<logolist.size(); i++)
				{
					if (!recursive)
						type = "IntegerList";
					intlist[i] = ((java.lang.Integer)logolist.get(i)).intValue();
				}
				return intlist;
    	   }
		}
		catch (Exception ex)
		{
			throw new ParseException("Java error in converting result: "+ex, 1);
		}
		return null;
	}
}