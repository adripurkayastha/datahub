package DataHubResources;

import DataHubORM.Column;

public class Constants {
	public static String SERVER_ADDR_ROOT = "datahub-experimental.csail.mit.edu";
	public static int SERVER_ADDR_PORT = 9000;
	
	//Main Field Names
	public static String SERVER_DB_CHECK_FIELD_NAME = "datname";
	
	public static String MODEL_TABLE_NAME_ATTRIBUTE = "tableName";
	
	public static String integerColumnName = "integerColumn";
	public static Column<Integer> integerColumn;

}
