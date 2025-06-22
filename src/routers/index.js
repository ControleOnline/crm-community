import {createNativeStackNavigator} from '@react-navigation/native-stack';
import loginRoutes from '@controleonline/ui-login/src/react/router/routes';
import crmRoutes from '@controleonline/ui-crm/src/react/router/routes';
import commonRoutes from '@controleonline/ui-common/src/react/router/routes';
import peopleRoutes from '@controleonline/ui-people/src/react/router/routes';
import customersRoutes from '@controleonline/ui-customers/src/react/router/routes';

const Stack = createNativeStackNavigator();

const allRoutes = [
  ...loginRoutes,
  ...crmRoutes,
  ...commonRoutes,
  ...peopleRoutes,
  ...customersRoutes,
];

export default function Routes() {
  return (
    <Stack.Navigator detachInactiveScreens={true}>
      {allRoutes.map((route, index) => (
        <Stack.Screen
          key={index}
          name={route.name}
          component={route.component}
          options={route.options}
          initialParams={route.initialParams}
        />
      ))}
    </Stack.Navigator>
  );
}
