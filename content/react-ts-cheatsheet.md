---
title: "React TypeScript Cheatsheet"
slug: react-typescript-cheatsheet
date: 11/05/2019
---

Here is the
[ESLint configuration](https://gist.github.com/Geospace/2a5fdbe7054afc3d210f60f12c5a5b03)
I'm using. TypeScript (TS) is about actually puting types so the use of `any`,
missing parameter types and missing return function types are forbidden.

I'm using Create React App, with the following packages:

```
"react": "^16.8.6",
"@types/react": "16.8.10",
"typescript": "^3.4.1",
```


## Function component, without logic nor props

This is the simplest case. Our component is a function that doesn't take
anything and only returns a block of JSX.

```tsx
const Component = (): JSX.Element => (
  <p>Hello, World!</p>
);
```

The only type annotation we need is the return type of the function:
`JSX.Element`, which is enforced by TS and **doesn't require any import** (as
long as the project is configured to use TS, of course).


## Function component, without logic

This case is very similar to the previous one. Our component still does not
implement any logic, but it takes props as parameters.

```tsx
interface Props {
  message: string;
}

const Component = (props: Props): JSX.Element => (
  <p>{props.message}</p>
);
```

We now also have to annotate our props. The keyword `type` might be used
instead of the `interface` one. However, I usually use it for type composition
only.

In case of a short type, the annotation may be **inline**:

```tsx
const Component = (props: { message: string }): JSX.Element => (
  ...
```

The props may also be **deconstructed**:

```tsx
const Component = ({ message }: { message: string }): JSX.Element => (
  ...
```

## `React.FunctionComponent`

`React.FunctionComponent` and `React.FC` are types describing a function
component. One could do:

```tsx
interface Props {
  message: string;
}

// Or React.FC
const Component: React.FunctionComponent<Props> = ({ message }: Props): JSX.Element => (
  <p>{ message }</p>
);
```

Because the configuration I use requires to annotate all the parameters and
return values, **the type signature is now duplicated**. Anyway, I think it's
better to put the annonations on the left and let the compiler deduce the
type on the right hand side. Moreover, these typenames may change in the future
so I will avoid **tying my code** to them.

The names `React.SFC` (Stateless Function(al ?) Component) and
`React.Stateless` are now **deprecated** and should not be used anymore.
See [some discussion](https://twitter.com/dan_abramov/status/1057625147216220162)
about it and
[the associated pull request](https://github.com/DefinitelyTyped/DefinitelyTyped/pull/30364).


## Going stateful

We now have a state:

```jsx
interface Props {
  message: string;
}

interface State {
  selected: boolean;
}

class Component extends React.Component<Props, State> {
  state = {
    selected: false
  };

  handleClick = () => {
    const { selected } = this.state;

    this.setState({
      selected: !selected,
    });
  };

  render = () => {
    const { handleClick } = this;
    const { message } = this.props;
    const { selected } = this.state;

    return (
      <Button onClick={handleClick} type={selected ? 'primary' : 'default'}>
        { message }
      </Button>
    );
  }
}
```

The state is annotated just like the props and the props are annotated as
before.

I'm taking advantage of the
[class field proposal](https://github.com/tc39/proposal-class-fields) to avoid
writing a constructor and still set my initial state. Also, **writing methods
as arrow functions** allows not to introduce a new `this` therefore avoiding
the `.bind()` problem.

If the **class component is stateless**, `React.Component` might have only
one type parameter:

```jsx
class Component extends React.Component<Props> {
  ...
```


## Dealing with Higher Order Components

An Higher Order Component (HOC) is all about injecting props into a component
so we will have to add a few annonations. Here is an example with
[React Router](https://reacttraining.com/react-router/web/guides/quick-start):

```tsx
import { withRouter, RouteComponentProps } from 'react-router-dom';


interface Props {
  message: string;
}

interface State {
  selected: string;
}

type AllProps = Props & RouteComponentProps;

class Component extends React.Component<AllProps, State> {
  state = {
    selected: false
  };

  handleClick = () => {
    const { selected } = this.state;

    this.setState({
      selected: !selected,
    });
  };

  render = () => {
    const { handleClick } = this;
    const { message, location } = this.props;
    const { selected } = this.state;

    return (
      <Button
        onClick={handleClick}
        type={selected ? 'primary' : 'default'}
        // Disable the button if the current URL includes 'banned'
        // (This is just an example...)
        disabled={!location.pathname.includes('banned')}
      >
        { message }
      </Button>
    );
  }
}

export default withRouter(Component);
```

Juste like in JavaScript (JS), we wrap our component definition with
`withRouter`. Then, we use type composition in order to create a new `AllProps`
type which is our `Props` **and** the ones exported by React Router. This
allows us to access `this.props.location` without any problem.

Sometimes, the exported props type requires a type parameter to work
properly. For example:

```tsx
import { withRouter, RouteComponentProps } from 'react-router-dom';

interface MatchParams {
  page: string;
}

type Props = RouteComponentProps<MatchParams>;

class ToBeValidated extends Component<Props, ToBeValidatedState> {
  ...
}

export default withRouter(Component);
```

Now we can access `this.props.match.params.page`.

Let's conclude with a few more or less related ressources:

* [TypeScript JSX Manual](https://www.typescriptlang.org/docs/handbook/jsx.html)
* [10++ TypeScript Pro tips/patterns with (or without) React](https://medium.com/@martin_hotell/10-typescript-pro-tips-patterns-with-or-without-react-5799488d6680)
* [How to better organize your React applications?](https://medium.com/@alexmngn/how-to-better-organize-your-react-applications-2fd3ea1920f1)
